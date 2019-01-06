# main file studying the evolution of the metrics on the belgian experiment pads
import config
from analytics import operation_builder
from analytics.parser import *
from analytics.visualization import *
import numpy as np
import pandas as pd
import os
import math
from sklearn.cluster import KMeans

list_of_elem_ops_per_pad = dict()
elemOpsCounter = 0

# root_of_dbs = "../belgian_experiment/"
root_of_dbs = "data/"
# Os walk among all the directories containing all the pads.
for (dirpath, dirnames, filenames) in os.walk(root_of_dbs):
    for filename in filenames:
        # if ".db" in filename:
        if '.sql' in filename:
            path_to_db = os.path.join(dirpath, filename)
            # Fetching the new operations
            # list_of_elem_ops_per_main, _ = get_elem_ops_per_pad_from_db(path_to_db=path_to_db, editor='etherpadSQLite3')
            list_of_elem_ops_per_main = get_elem_ops_per_pad_from_db(
                path_to_db=path_to_db,
                editor='sql_dump'
                # editor = 'etherpad'
            )  # we got the ElementOperations of each pad at beginining
            # the pad extracted from each file always have the same name so we give them a new name based on their path
            pad_name = path_to_db[len(root_of_dbs):path_to_db.find("data") - 1]
            # We check that there is only one pad per file as there should be (one pad per session)
            assert len(list_of_elem_ops_per_main.keys()) == 1
            # we rename it
            list_of_elem_ops_per_pad[pad_name] = list_of_elem_ops_per_main['main']

# We create the operation from the list of elementary operations
pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad,
                                                                             config.maximum_time_between_elem_ops)


def find_start(pad):
    """
    Find the index of the Operation where writers start the pad.

    :return:
    """
    elem_ops = pad.get_elem_ops(sorted_=True)
    delays = []
    first = True
    for i, elem_op in enumerate(elem_ops):
        if not first:
            delays.append(elem_ops[i].timestamp - elem_ops[i - 1].timestamp)
        first = False

    delays = np.array(delays).reshape((-1,1))
    print(delays)
    kmeans = KMeans(2)
    kmeans.fit(delays)
    labels = np.array(kmeans.labels_)
    print(labels)
    return elem_ops[np.where(labels>0)[0][0]+1].timestamp


# Initialize the dataframe storing all results
df = pd.DataFrame()

for pad_name in pads:
    pad = pads[pad_name]

    # Find the time of the start and the end of the pad
    num_splits = 32
    zoom_proportion = 14 / 15
    timestamps = [x.timestamp for x in pad.get_elem_ops(sorted_=False)]
    start_time = min(timestamps)
    end_time = max(timestamps)
    all_thresholds = np.linspace(start_time, end_time, num_splits + 1)

    # the essay writing started 120min before the last op
    start_time = end_time - 7.2e+6
    thresholds = np.linspace(start_time, end_time, num_splits + 1)
    if pad_name == 'Group 1_session 1':
        thresholds = np.linspace(all_thresholds[math.ceil(num_splits*28/30)], all_thresholds[math.ceil(num_splits*30/30)], num_splits + 1)
    elif pad_name == 'Group 3_session 1':
        thresholds = np.linspace(all_thresholds[math.ceil(num_splits*28/30)], all_thresholds[math.ceil(num_splits*30/30)], num_splits + 1)
    elif pad_name == 'Group 9_session 1':
        thresholds = np.linspace(all_thresholds[math.ceil(num_splits*16/30)], all_thresholds[math.ceil(num_splits*19/30)], num_splits + 1)

    # Initialize the metric scores for this pad
    splits_name = []
    user_participation_paragraph_score_list = []
    prop_score_list = []
    sync_score_list = []
    alternating_score_list = []
    break_score_day_list = []
    break_score_short_list = []
    type_overall_score_write_list = []
    type_overall_score_delete_list = []
    type_overall_score_edit_list = []
    type_overall_score_paste_list = []
    user_type_score_delete_list = []
    user_type_score_edit_list = []
    user_type_score_write_list = []
    user_type_score_paste_list = []

    # we will study the evolution of the metrics over time per pad. So we split the pad in different pads all
    # corresponding to a different point in time
    for num_th, threshold in enumerate(all_thresholds[1:]):
        # Create the names for the splits
        split_name = str(num_th+1)+'/'+str(num_splits)
        splits_name.append(split_name)

        # Create a new pad corresponding to a pad at a certain time
        new_pad, new_elem_ops = pad.pad_at_timestamp(threshold)

        # create the paragraphs
        new_pad.create_paragraphs_from_ops(new_elem_ops)
        # classify the operations of the pad
        new_pad.classify_operations(length_edit=config.length_edit, length_delete=config.length_delete)
        # find the context of the operation of the pad
        new_pad.build_operation_context(config.delay_sync, config.time_to_reset_day, config.time_to_reset_break)

        print("PAD %s at %s of the end:" % (pad_name, split_name))

        print('\nCOLORED TEXT BY AUTHOR')
        print(new_pad.display_text_colored_by_authors())

        # Get all the metrics
        user_participation_paragraph_score = new_pad.user_participation_paragraph_score()
        user_participation_paragraph_score_list.append(user_participation_paragraph_score)
        prop_score = new_pad.prop_score()
        prop_score_list.append(prop_score)
        sync_score = new_pad.sync_score()[0]
        sync_score_list.append(sync_score)
        alternating_score = new_pad.alternating_score()
        alternating_score_list.append(alternating_score)
        break_score_day = new_pad.break_score('day')
        break_score_day_list.append(break_score_day)
        break_score_short = new_pad.break_score('short')
        break_score_short_list.append(break_score_short)
        type_overall_score_write = new_pad.type_overall_score('write')
        type_overall_score_write_list.append(type_overall_score_write)
        type_overall_score_paste = new_pad.type_overall_score('paste')
        type_overall_score_paste_list.append(type_overall_score_paste)
        type_overall_score_delete = new_pad.type_overall_score('delete')
        type_overall_score_delete_list.append(type_overall_score_delete)
        type_overall_score_edit = new_pad.type_overall_score('edit')
        type_overall_score_edit_list.append(type_overall_score_edit)
        user_type_score_write = new_pad.user_type_score('write')
        user_type_score_write_list.append(user_type_score_write)
        user_type_score_paste = new_pad.user_type_score('paste')
        user_type_score_paste_list.append(user_type_score_paste)
        user_type_score_delete = new_pad.user_type_score('delete')
        user_type_score_delete_list.append(user_type_score_delete)
        user_type_score_edit = new_pad.user_type_score('edit')
        user_type_score_edit_list.append(user_type_score_edit)

    # Fill the dataframe for this pad with all its scores
    df_pad = pd.DataFrame()
    df_pad['pad_name'] = [pad_name]*num_splits
    df_pad['time'] = splits_name
    df_pad['User proportion per paragraph score'] = user_participation_paragraph_score_list
    df_pad['Proportion score'] = prop_score_list
    df_pad['Synchronous score'] = sync_score_list
    df_pad['Alternating score'] = alternating_score_list
    df_pad['Break score day'] = break_score_day_list
    df_pad['Break score short'] = break_score_short_list
    df_pad['Overall write type score'] = type_overall_score_write_list
    df_pad['Overall paste type score'] = type_overall_score_paste_list
    df_pad['Overall delete type score'] = type_overall_score_delete_list
    df_pad['Overall edit type score'] = type_overall_score_edit_list
    df_pad['User write score'] = user_type_score_write_list
    df_pad['User paste score'] = user_type_score_paste_list
    df_pad['User delete score'] = user_type_score_delete_list
    df_pad['User edit score'] = user_type_score_edit_list
    df = pd.concat([df, df_pad])

# save the plot of the results
for metric in df.columns[2:]:
    # save the distribution for all pads on the same plot
    display_boxplot_split(df, metric, save_location=config.figs_save_location)
    for pad_name in pads:
        # save the distributions for each pads
        display_barplot_split(df[df['pad_name'] == pad_name], metric, pad_name, save_location=config.figs_save_location)
