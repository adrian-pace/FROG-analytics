# Main file computing the metric and visualizations for Stian's logs
from analytics import operation_builder
from analytics import parser
import config
from analytics import Operations
from analytics.visualization import *


path_to_db = "../stian logs/store.csv"
# We fetch the elementary operations
list_of_elem_ops_per_pad, _ = parser.get_elem_ops_per_pad_from_db(path_to_db, 'stian_logs')
print(list_of_elem_ops_per_pad.keys())
print(len(list_of_elem_ops_per_pad.keys()))

# The aTextes were used in debug to check whether we had the same results after recomputing the text from the elementary operations
# TODO remove ?
aTextes = dict()
with open("../stian logs/store.csv", encoding='utf-8') as f:
    lines = f.readlines()
for line in lines:
    if ',"{""atext"":{""text"":""' in line:
        pad = line[len("pad:"):line.find(',"{""atext"":{""text"":""')]
        aTextes[pad] = line[line.find(',"{""atext"":{""text"":""') + len(',"{""atext"":{""text"":""'):line.find(
            '"",""attribs"":""')]

# We usually study only a subset of the pads so that its faster
subset_of_keys = list(list_of_elem_ops_per_pad.keys())[:150]
new_list_of_elem_ops_per_pad = dict()
for key in subset_of_keys:
    new_list_of_elem_ops_per_pad[key] = list_of_elem_ops_per_pad[key]

# Comment this line if you don't want a subset
list_of_elem_ops_per_pad = new_list_of_elem_ops_per_pad

# Uncomment if you want to study a specific pad
# list_of_elem_ops_per_pad = {"753268753268753268753268753268753268": list_of_elem_ops_per_pad["753268753268753268753268753268753268"]}

# We need the elmentary operation sorted. They should be sorted anyway since we sort them when we get them
list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(list_of_elem_ops_per_pad)

# We build the operations from the elementary operations
pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad_sorted,
                                                                             config.maximum_time_between_elem_ops)

# For all the pads, we create the paragraphs, classify the operations and compute their context
for pad_name in pads:
    pad = pads[pad_name]
    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
    # classify the operations of the pad
    pad.classify_operations(length_edit=config.length_edit, length_delete=config.length_delete)
    # find the context of the operation of the pad
    pad.build_operation_context(config.delay_sync, config.time_to_reset_day, config.time_to_reset_break)

print(len(pads))
# For each pad, we check that by reconstructing it, it is indeed what it should be. We also display the metrics and
# save visualizations.
for pad_name in pads:
    pad = pads[pad_name]
    print("PAD:", pad_name)
    text = pad.get_text()
    # print(text)
    text = text.strip('\n')
    aText = aTextes[pad_name].replace("\\n", "\n").replace('\\""', '"').strip('\n')
    if text != aText:
        print("TEXT:")
        print(text)
        print("aText:")
        print(aText)
        print("With n_elem_ops", len(pad.get_elem_ops(sorted_=False)))

    print('\nCOLORED TEXT BY AUTHOR')
    print(pad.display_text_colored_by_authors())

    # print('\nCOLORED TEXT BY OPS')
    # print(pad.display_text_colored_by_ops())

    print('\nSCORES')
    print('User proportion per paragraph score', pad.user_participation_paragraph_score())
    print('Proportion score:', pad.prop_score())
    print('Synchronous score:', pad.sync_score()[0])
    print('Alternating score:', pad.alternating_score())
    print('Break score day:', pad.break_score('day'))
    print('Break score short:', pad.break_score('short'))
    print('Overall write type score:', pad.type_overall_score('write'))
    print('Overall paste type score:', pad.type_overall_score('paste'))
    print('Overall delete type score:', pad.type_overall_score('delete'))
    print('Overall edit type score:', pad.type_overall_score('edit'))
    print('User write score:', pad.user_type_score('write'))
    print('User paste score:', pad.user_type_score('paste'))
    print('User delete score:', pad.user_type_score('delete'))
    print('User edit score:', pad.user_type_score('edit'))

    display_user_participation(pad, config.figs_save_location)
    display_user_participation_paragraphs_with_del(pad, config.figs_save_location)

    # plot the proportion of synchronous writing per paragraphs
    display_proportion_sync_in_paragraphs(pad, config.figs_save_location)

    # plot the overall type counts
    display_overall_op_type(pad, config.figs_save_location)

    # plot the counts of type per users
    display_types_per_user(pad, config.figs_save_location)
