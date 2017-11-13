from analytics import operation_builder
from analytics import parser
import config
from analytics import Operations
from analytics.visualization import *

# path_to_csv = "..\\stian logs\\store.csv"
# list_of_elem_ops_per_pad = get_elem_ops_per_pad_from_ether_csv(path_to_csv)
path_to_db = "../stian logs/store.csv"
list_of_elem_ops_per_pad = parser.get_elem_ops_per_pad_from_ether_csv(path_to_db)
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

#list_of_elem_ops_per_pad = {"386650386650386650386650386650386650": list_of_elem_ops_per_pad["386650386650386650386650386650386650"]}

list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(list_of_elem_ops_per_pad)

maximum_time_between_elem_ops = 20000  # milliseconds
pads = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad_sorted,
                                                        maximum_time_between_elem_ops,
                                                        config.delay_sync,
                                                        config.time_to_reset_day,
                                                        config.time_to_reset_break,
                                                        config.length_edit,
                                                        config.length_delete)
print(len(pads))
for pad_name in pads:
    pad = pads[pad_name]
    print("PAD:", pad_name)
    text = pad.get_text()
    #print(text)
    text=text.strip('\n')
    aText = aTextes[pad_name].replace("\\n", "\n").replace('\\""', '"').strip('\n')
    print(text == aText)
    if text != aText:
        print("TEXT:")
        print(text)
        print("aText:")
        print(aText)
        print("With n_elem_ops", len(pad.get_all_elementary_operation()))


    #print('\nCOLORED TEXT BY AUTHOR')
    #pad.display_text_colored_by_authors()

    #print('\nCOLORED TEXT BY OPS')
    #pad.display_text_colored_by_ops()
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
