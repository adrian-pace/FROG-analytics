import requests
from pprint import pprint
from flask import Flask, jsonify
from flask import request as flask_request
import threading
from multiprocessing import Queue
import time
from analytics import parser, operation_builder
import config

app = Flask(__name__)

analytics_started = False
analytic_thread = None
updates_thread = None
queueLock = threading.Lock()
workQueue = Queue(1)
last_answer = None


class AnalyticThread(threading.Thread):
	"""
	Thread running parsing and calculating the metrics for each pad
	"""
    def __init__(self, name, pad_names, regex, workQueue, queueLock, update_delay):
		"""
		Initialize the thread worker
		
		:param name: name of the thread worker
		:param pad_names: the pad names we want to study
		:param regex: the regex we want the name of the pads to match
		:param workQueue: where we store the metrics
		:param queueLock: lock to access the queue
		:param update_delay: how much time to wait between checking for new operations
		"""
        threading.Thread.__init__(self)
        self.update_delay = update_delay
        self.regex = regex
        self.name = name
        self.pad_names = pad_names
        self.workQueue = workQueue
        self.queueLock = queueLock

    def run(self):
        print("Starting", self.name)
        revs_mongo = dict()
        answer = dict()
        for pad_name in self.pad_names:
			# At first we want the pads from the begining.
            revs_mongo[pad_name] = 0

        dic_author_current_operations_per_pad = dict()
        pads = dict()
        while analytics_started:
			# Parse the elementary operations from the FROG database
            new_list_of_elem_ops_per_pad, revs_mongo = parser.get_elem_ops_per_pad_from_db(None,
                                                                                           'FROG',
                                                                                           revs_mongo=revs_mongo,
                                                                                           regex=self.regex)
            if len(new_list_of_elem_ops_per_pad) != 0:
				# If we have new ops
                new_list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(
                    new_list_of_elem_ops_per_pad)
                pads, dic_author_current_operations_per_pad, elem_ops_treated = operation_builder.build_operations_from_elem_ops(
                    new_list_of_elem_ops_per_pad_sorted, config.maximum_time_between_elem_ops,
                    dic_author_current_operations_per_pad, pads)
				# For each pad, create the paragraphs, classify the operations and create the context
                for pad_name in elem_ops_treated:
                    pad = pads[pad_name]
                    # create the paragraphs
                    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
                    # classify the operations of the pad
                    pad.classify_operations(length_edit=config.length_edit, length_delete=config.length_delete)
                    # find the context of the operation of the pad
                    pad.build_operation_context(config.delay_sync, config.time_to_reset_day,
                                                config.time_to_reset_break)
				# We then calculate the metrics for each pad that changed
                for pad_name in elem_ops_treated:
                    print(pad_name)
                    pad = pads[pad_name]
                    answer_per_pad = dict()
                    answer_per_pad['User proportion per paragraph score'] = pad.user_participation_paragraph_score()
                    answer_per_pad['Proportion score:'] = pad.prop_score()
                    answer_per_pad['Synchronous score:'] = pad.sync_score()[0]
                    answer_per_pad['Alternating score:'] = pad.alternating_score()
                    answer_per_pad['Break score day:'] = pad.break_score('day')
                    answer_per_pad['Break score short:'] = pad.break_score('short')
                    answer_per_pad['Overall write type score:'] = pad.type_overall_score('write')
                    answer_per_pad['Overall paste type score:'] = pad.type_overall_score('paste')
                    answer_per_pad['Overall delete type score:'] = pad.type_overall_score('delete')
                    answer_per_pad['Overall edit type score:'] = pad.type_overall_score('edit')
                    answer_per_pad['User write score:'] = pad.user_type_score('write')
                    answer_per_pad['User paste score:'] = pad.user_type_score('paste')
                    answer_per_pad['User delete score:'] = pad.user_type_score('delete')
                    answer_per_pad['User edit score:'] = pad.user_type_score('edit')
                    pprint(answer_per_pad)
                    answer_per_pad['text'] = pad.get_text()
                    answer_per_pad['text_colored_by_authors'] = pad.display_text_colored_by_authors()
                    answer_per_pad['text_colored_by_ops'] = pad.display_text_colored_by_ops()
                    print(answer_per_pad['text'])
                    answer[pad_name] = answer_per_pad
            time.sleep(self.update_delay)
            self.queueLock.acquire()
            if self.workQueue.full():
                queuer = self.workQueue.get()
                for pad_name in answer:
                    queuer[pad_name] = answer[pad_name]
                self.workQueue.put(queuer)
            else:
                self.workQueue.put(answer)
            self.queueLock.release()
        print('exiting', self.name)


class UpdatesThread(threading.Thread):
	"""
	worker thread that send the metrics by HTTP/POST .
	"""
    def __init__(self, thread_name, url, update_delay, workQueue, queueLock):
		"""
		Instantiate the thread worker that sends the metrics
		
		:param thread_name: the name of the thread worker
		:param url: url to which we should send the metrics
		:param update_delay: How much time we wait before sending the update again.
		:param workQueue: where the metrics are stored
		:param queueLock:  lock to access the queue
		"""
        threading.Thread.__init__(self)
        self.update_delay = update_delay
        self.url = url
        self.thread_name = thread_name
        self.workQueue = workQueue
        self.queueLock = queueLock

    def run(self):
        global last_answer
        while analytics_started:
			# if the queue is not empty (it has been updated)
            if not self.workQueue.empty():
                self.queueLock.acquire()
                last_answer = workQueue.get()
                self.queueLock.release()
				# send the metrics
                requests.post(url=self.url, json=last_answer)
            time.sleep(self.update_delay)


@app.route('/', methods=['GET', 'POST'])
def receiving_requests():
	"""
	is triggered when we receive a post request.
	"""
	
    global analytics_started
    global analytic_thread
    global updates_thread
    global queueLock
    global workQueue
    global last_answer
    if flask_request.method == 'POST':
		# The json contains which pads are of interest to us.
        json = flask_request.get_json()
        if 'pad_names' in json:
            pad_names = json['pad_names']
        else:
            pad_names = []
        if 'regex' in json:
            regex = json['regex']
        else:
            regex = None
		# When we get a post, we stop the running threads and start new ones looking for the new pads
        if analytics_started:
            print("Exiting analytics threads with old pad names")
            analytics_started = False
            analytic_thread.join()
            # TODO uncomment
            #updates_thread.join()
            print("Analytics threads stopped with old pad names")
        workQueue = Queue(1)
        queueLock = threading.Lock()
		# We start the new threads that have the new parameters
        analytic_thread = AnalyticThread("Analytics thread", pad_names, regex, workQueue, queueLock, config.server_update_delay)
        updates_thread = UpdatesThread("Updates thread", config.update_post_url, config.send_update_delay, workQueue,
                                       queueLock)
        analytics_started = True
        analytic_thread.start()
        # TODO uncomment
        updates_thread.start()
        return "Analytics started", 200

    # TODO remove
    elif flask_request.method == 'GET':
        if workQueue.empty() and last_answer is None:
            return 'Data Not yet available', 503
        elif not workQueue.empty():
            queueLock.acquire()
            last_answer = workQueue.get()
            queueLock.release()
        return jsonify(last_answer), 200
