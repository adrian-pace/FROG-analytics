from analytics import operation_builder
from analytics import parser
import config
from analytics import Operations
from analytics.visualization import *

# path_to_csv = "..\\stian logs\\store.csv"
# list_of_elem_ops_per_pad = get_elem_ops_per_pad_from_ether_csv(path_to_csv)


path_to_db = "../stian logs/store.csv"
list_of_elem_ops_per_pad,_ = parser.get_elem_ops_per_pad_from_db(path_to_db,'stian_logs')
print(list_of_elem_ops_per_pad.keys())
print(len(list_of_elem_ops_per_pad.keys()))

aTextes = dict()
with open("../stian logs/store.csv", encoding='utf-8') as f:
    lines = f.readlines()
for line in lines:
    if ',"{""atext"":{""text"":""' in line:
        pad = line[len("pad:"):line.find(',"{""atext"":{""text"":""')]
        aTextes[pad] = line[line.find(',"{""atext"":{""text"":""') + len(',"{""atext"":{""text"":""'):line.find(
            '"",""attribs"":""')]

subset_of_keys = list(list_of_elem_ops_per_pad.keys())[:150]
new_list_of_elem_ops_per_pad = dict()
for key in subset_of_keys:
    new_list_of_elem_ops_per_pad[key] = list_of_elem_ops_per_pad[key]

list_of_elem_ops_per_pad = new_list_of_elem_ops_per_pad

#list_of_elem_ops_per_pad = {"753268753268753268753268753268753268": list_of_elem_ops_per_pad["753268753268753268753268753268753268"]}

list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(list_of_elem_ops_per_pad)

pads,_,elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad_sorted,
                                                        config.maximum_time_between_elem_ops)

for pad_name in pads:
    pad=pads[pad_name]
    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
    # classify the operations of the pad
    pad.classify_operations(length_edit=config.length_edit,length_delete=config.length_delete)
    # find the context of the operation of the pad
    pad.build_operation_context(config.delay_sync, config.time_to_reset_day,config.time_to_reset_break)

print(len(pads))
for pad_name in pads:
    pad = pads[pad_name]
    print("PAD:", pad_name)
    text = pad.get_text()
    #print(text)
    text=text.strip('\n')
    aText = aTextes[pad_name].replace("\\n", "\n").replace('\\""', '"').strip('\n')
    if text != aText:
        print("TEXT:")
        print(text)
        print("aText:")
        print(aText)
        print("With n_elem_ops", len(pad.get_all_elementary_operation()))


    print('\nCOLORED TEXT BY AUTHOR')
    print(pad.display_text_colored_by_authors())

    #print('\nCOLORED TEXT BY OPS')
    #print(pad.display_text_colored_by_ops())

    print('\nSCORES')
    print('User proportion per paragraph score', pad.user_participation_paragraph_score())
    print('Proportion score:', pad.prop_score())
    print('Synchronous score:', pad.sync_score()[0])
    print('Alternating score:', pad.alternating_score())
    print('Break score day:', pad.break_score('day'))
    print('Break score short:', pad.break_score('short'))

    display_user_participation(pad)
    display_user_participation_paragraphs_with_del(pad)

    # plot the proportion of synchronous writing per paragraphs
    display_proportion_sync_in_paragraphs(pad)

    # plot the overall type counts
    display_overall_op_type(pad)

    # plot the counts of type per users
    display_types_per_user(pad)
    #
    # print("ops:")
    # for op in pad.operations:
    #     print(op)
    #     print("\n")
    #
    # print("\nElem_ops")
    # for elem_op in pad.get_all_elementary_operation():
    #     if elem_op.timestamp>1436594858000 and elem_op.timestamp<1436594859406:
    #         print(elem_op)
    #         print("\n")


    # after 1436594858406 before 1436594868772
    # print(pad.get_text(1436594858000))





    # plot the participation proportion per user per paragraphs
    #display_user_participation_paragraphs(pad)

    # plot the proportion of synchronous writing per paragraphs
    #display_proportion_sync_in_paragraphs(pad)

    # plot the overall type counts
    #display_overall_op_type(pad)

    # plot the counts of type per users
    #display_types_per_user(pad)

    # print('OPERATIONS')
    # pad.display_operations()

    # print("PARAGRAPHS:")
    # pad.display_paragraphs(verbose=1)
