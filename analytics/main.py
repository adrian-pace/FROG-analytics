import operation_builder
from analytics.operation_builder import build_operations_from_elem_ops
from analytics.parser import *
from analytics.visualization import *
import config

# path_to_csv = "..\\stian logs\\store.csv"
# list_of_elem_ops_per_pad = get_elem_ops_per_pad_from_ether_csv(path_to_csv)
path_to_db = "..\\etherpad\\var\\dirty.db"

list_of_elem_ops_per_pad, _ = get_elem_ops_per_pad_from_db(path_to_db=path_to_db, editor='etherpad')
# list_of_elem_ops_per_pad,_ = get_elem_ops_per_pad_from_db(editor='collab-react-components')

pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad,
                                                                             config.maximum_time_between_elem_ops)

for pad_name in pads:
    pad = pads[pad_name]
    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
    # classify the operations of the pad
    pad.classify_operations(length_edit=config.length_edit, length_delete=config.length_delete)
    # find the context of the operation of the pad
    pad.build_operation_context(config.delay_sync, config.time_to_reset_day, config.time_to_reset_break)

for pad_name in pads:
    pad = pads[pad_name]
    print("PAD:", pad_name)
    print("TEXT:")
    print(pad.get_text())

    print('\nCOLORED TEXT BY AUTHOR')
    print(pad.display_text_colored_by_authors())

    print('\nCOLORED TEXT BY OPS')
    print(pad.display_text_colored_by_ops())

    print('\nSCORES')
    print('User proportion per paragraph score', pad.user_participation_paragraph_score())
    print('Proportion score:', pad.prop_score())
    print('Synchronous score:', pad.sync_score()[0])
    print('Alternating score:', pad.alternating_score())
    print('Break score day:', pad.break_score('day'))
    print('Break score short:', pad.break_score('short'))

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
