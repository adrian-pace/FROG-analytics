import config
import operation_builder
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

for pad_name in pads:
    pad = pads[pad_name]
    to_print = "PAD:" + pad_name + "\n" \
               + "TEXT:\n" + pad.get_text() + "\n" \
               + '\nCOLORED TEXT BY AUTHOR\n' + pad.display_text_colored_by_authors() + "\n" \
               + '\nCOLORED TEXT BY OPS\n' + pad.display_text_colored_by_ops() + "\n" \
               + '\nSCORES' \
               + '\nUser proportion per paragraph score:' + str(pad.user_participation_paragraph_score()) \
               + '\nProportion score:' + str(pad.prop_score()) \
               + '\nSynchronous score:' + str(pad.sync_score()[0]) \
               + '\nAlternating score:' + str(pad.alternating_score()) \
               + '\nBreak score day:' + str(pad.break_score('day')) \
               + '\nBreak score short:' + str(pad.break_score('short'))
    print(to_print)
    with open("texts/"+pad_name+".txt","w+",encoding='utf-8') as f:
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

    # print('OPERATIONS')
    #   pad.display_operations()

    # print("PARAGRAPHS:")
    #   pad.display_paragraphs(verbose=1)
