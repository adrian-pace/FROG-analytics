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
myThread = None
queueLock = threading.Lock()
workQueue = Queue(1)
last_answer = None


class AnalyticThread(threading.Thread):
    def __init__(self, name, pad_names, regex, workQueue, queueLock):
        threading.Thread.__init__(self)
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
            revs_mongo[pad_name] = 0

        dic_author_current_operations_per_pad = dict()
        pads = dict()
        while analytics_started:
            new_list_of_elem_ops_per_pad, revs_mongo = parser.get_elem_ops_per_pad_from_db(None,
                                                                                           'collab-react-components',
                                                                                           revs_mongo=revs_mongo,
                                                                                           regex=self.regex)
            if len(new_list_of_elem_ops_per_pad) != 0:
                new_list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(
                    new_list_of_elem_ops_per_pad)
                pads, dic_author_current_operations_per_pad, elem_ops_treated = operation_builder.build_operations_from_elem_ops(
                    new_list_of_elem_ops_per_pad_sorted, config.maximum_time_between_elem_ops,
                    dic_author_current_operations_per_pad, pads)
                # TODO All the parsing and operation building is done on pads we don't want !
                for pad_name in elem_ops_treated:
                    pad = pads[pad_name]
                    # create the paragraphs
                    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
                    # classify the operations of the pad
                    pad.classify_operations(length_edit=config.length_edit, length_delete=config.length_delete)
                    # find the context of the operation of the pad
                    pad.build_operation_context(config.delay_sync, config.time_to_reset_day,
                                                config.time_to_reset_break)

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
            time.sleep(0.5)
            queueLock.acquire()
            if workQueue.full():
                queuer = workQueue.get()
                for pad_name in answer:
                    queuer[pad_name] = answer[pad_name]
                workQueue.put(queuer)
            else:
                workQueue.put(answer)
            queueLock.release()
        print('exiting', self.name)


@app.route('/', methods=['GET', 'POST'])
def receiving_data():
    global analytics_started
    global myThread
    global queueLock
    global workQueue
    global last_answer
    if flask_request.method == 'POST':
        json = flask_request.get_json()
        if 'pad_names' in json:
            pad_names = json['pad_names']
        else:
            pad_names = []
        if 'regex' in json:
            regex = json['regex']
        else:
            regex = None
        if analytics_started:
            print("Exiting analytics thread with old pad names")
            analytics_started = False
            myThread.join()
            print("Analytics stopped with old pad names")
        workQueue = Queue(1)
        queueLock = threading.Lock()
        myThread = AnalyticThread("Analytics_thread", pad_names, regex, workQueue, queueLock)
        analytics_started = True
        myThread.start()
        return "Analytics started", 200
    elif flask_request.method == 'GET':
        if workQueue.empty() and last_answer is None:
            return 'Data Not yet available', 503
        elif not workQueue.empty():
            queueLock.acquire()
            last_answer = workQueue.get()
            queueLock.release()
        return jsonify(last_answer), 200
