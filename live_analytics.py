import config
from analytics import operation_builder
from analytics import parser
import time

index_from = 0
dic_author_current_operations_per_pad = dict()
pads = dict()
revs_mongo = None
while True:
    if config.editor == 'etherpad':
        new_list_of_elem_ops_per_pad, index_from = parser.get_elem_ops_per_pad_from_db(config.path_to_db,
                                                                                       'etherpad',
                                                                                       index_from_lines=index_from)
    else:
        new_list_of_elem_ops_per_pad, revs_mongo = parser.get_elem_ops_per_pad_from_db(None,
                                                                                       editor=config.editor,
                                                                                       revs_mongo=revs_mongo,
                                                                                       regex='^editor')

    if len(new_list_of_elem_ops_per_pad) != 0:
        # sort them by their timestamps, even though they should already be sorted
        new_list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(new_list_of_elem_ops_per_pad)

        # Create the operations from the elementary operations
        pads, dic_author_current_operations_per_pad, elem_ops_treated = operation_builder.build_operations_from_elem_ops(
            new_list_of_elem_ops_per_pad_sorted, config.maximum_time_between_elem_ops,
            dic_author_current_operations_per_pad, pads)

        # For each pad, create the paragraphs, classify the operations and create the context
        for pad_name in elem_ops_treated:
            pad = pads[pad_name]
            pad.create_content(
                elem_ops_treated[pad_name],
                config.length_edit,
                config.length_delete,
                config.delay_sync,
                config.time_to_reset_day,
                config.time_to_reset_break
            )

        # For each pad, calculate the metrics
        for pad_name in pads:
            pad = pads[pad_name]
            print(pad.to_print())
            print('\n\n\n')

    time.sleep(config.server_update_delay)
