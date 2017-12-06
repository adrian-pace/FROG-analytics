import config
from analytics import operation_builder
from analytics.parser import *
from analytics.visualization import *
import os

list_of_elem_ops_per_pad = dict()
elemOpsCounter = 0
root_of_dbs = "../belgian_experiment/"
for (dirpath, dirnames, filenames) in os.walk(root_of_dbs):
    for filename in filenames:
        if ".db" in filename:
            path_to_db = os.path.join(dirpath, filename)
            list_of_elem_ops_per_main, _ = get_elem_ops_per_pad_from_db(path_to_db=path_to_db, editor='etherpadSQLite3')
            pad_name = path_to_db[len(root_of_dbs):path_to_db.find("data") - 1]
            assert len(list_of_elem_ops_per_main.keys()) == 1
            list_of_elem_ops_per_pad[pad_name] = list_of_elem_ops_per_main['main']

pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad,
                                                                             config.maximum_time_between_elem_ops)

for pad_name in pads:
    elemOpsCounter += len(elem_ops_treated[pad_name])
    pad = pads[pad_name]
    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
    # classify the operations of the pad
    pad.classify_operations(length_edit=config.length_edit, length_delete=config.length_delete)
    # find the context of the operation of the pad
    pad.build_operation_context(config.delay_sync, config.time_to_reset_day, config.time_to_reset_break)

print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))

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

for pad_name in pads:
    pad = pads[pad_name]
    user_participation_paragraph_score = pad.user_participation_paragraph_score()
    user_participation_paragraph_score_list.append(user_participation_paragraph_score)
    prop_score = pad.prop_score()
    prop_score_list.append(prop_score)
    sync_score = pad.sync_score()[0]
    sync_score_list.append(sync_score)
    alternating_score = pad.alternating_score()
    alternating_score_list.append(alternating_score)
    break_score_day = pad.break_score('day')
    break_score_day_list.append(break_score_day)
    break_score_short = pad.break_score('short')
    break_score_short_list.append(break_score_short)
    type_overall_score_write = pad.type_overall_score('write')
    type_overall_score_write_list.append(type_overall_score_write)
    type_overall_score_paste = pad.type_overall_score('paste')
    type_overall_score_paste_list.append(type_overall_score_paste)
    type_overall_score_delete = pad.type_overall_score('delete')
    type_overall_score_delete_list.append(type_overall_score_delete)
    type_overall_score_edit = pad.type_overall_score('edit')
    type_overall_score_edit_list.append(type_overall_score_edit)
    user_type_score_write = pad.user_type_score('write')
    user_type_score_write_list.append(user_type_score_write)
    user_type_score_paste = pad.user_type_score('paste')
    user_type_score_paste_list.append(user_type_score_paste)
    user_type_score_delete = pad.user_type_score('delete')
    user_type_score_delete_list.append(user_type_score_delete)
    user_type_score_edit = pad.user_type_score('edit')
    user_type_score_edit_list.append(user_type_score_edit)

    to_print = "PAD:" + pad_name + "\n" \
               + "TEXT:\n" + pad.get_text() + "\n" \
               + '\nCOLORED TEXT BY AUTHOR\n' + pad.display_text_colored_by_authors() + "\n" \
               + '\nCOLORED TEXT BY OPS\n' + pad.display_text_colored_by_ops() + "\n" \
               + '\nSCORES' \
               + '\nUser proportion per paragraph score:' + str(user_participation_paragraph_score) \
               + '\nProportion score:' + str(prop_score) \
               + '\nSynchronous score:' + str(sync_score) \
               + '\nAlternating score:' + str(alternating_score) \
               + '\nBreak score day:' + str(break_score_day) \
               + '\nBreak score short:' + str(break_score_short) \
               + '\nOverall write type score:' + str(type_overall_score_write) \
               + '\nOverall paste type score:' + str(type_overall_score_paste) \
               + '\nOverall delete type score:' + str(type_overall_score_delete) \
               + '\nOverall edit type score:' + str(type_overall_score_edit) \
               + '\nUser write score:' + str(user_type_score_write) \
               + '\nUser paste score:' + str(user_type_score_paste) \
               + '\nUser delete score:' + str(user_type_score_delete) \
               + '\nUser edit score:' + str(user_type_score_edit)
    print(to_print)
    with open("texts/" + pad_name + ".txt", "w+", encoding='utf-8') as f:
        f.write(to_print)

    display_user_participation(pad, config.figs_save_location)
    # plot the participation proportion per user per paragraphs
    display_user_participation_paragraphs(pad, config.figs_save_location)
    display_user_participation_paragraphs_with_del(pad, config.figs_save_location)

    # plot the proportion of synchronous writing per paragraphs
    display_proportion_sync_in_paragraphs(pad, config.figs_save_location)

    # plot the overall type counts
    display_overall_op_type(pad, config.figs_save_location)

    # plot the counts of type per users
    display_types_per_user(pad, config.figs_save_location)

display_box_plot([user_participation_paragraph_score_list], ['user_participation_paragraph_score_list'])
display_box_plot([prop_score_list], ['prop_score_list'])
display_box_plot([sync_score_list], ['sync_score_list'])
display_box_plot([alternating_score_list], ['alternating_score_list'])
display_box_plot([break_score_day_list, break_score_short_list], ['break_score_day_list', 'break_score_short_list'])
display_box_plot([type_overall_score_write_list, type_overall_score_delete_list, type_overall_score_edit_list,
                  type_overall_score_paste_list],
                 ['type_overall_score_write_list', 'type_overall_score_delete_list', 'type_overall_score_edit_list',
                  'type_overall_score_paste_list'])
display_box_plot(
    [user_type_score_delete_list, user_type_score_edit_list, user_type_score_write_list, user_type_score_paste_list],
    ['user_type_score_delete_list', 'ser_type_score_edit_list', 'user_type_score_write_list',
     'user_type_score_paste_list'])
