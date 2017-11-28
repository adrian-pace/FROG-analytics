import argparse
from analytics import parser, operation_builder, visualization
import config

cl_parser = argparse.ArgumentParser(description="Run the analytics.")
cl_parser.add_argument("-p", "--path_to_db",
                       help="path to database storing the edits",
                       default=None)
cl_parser.add_argument("-e", "--editor",
                       help="What editor are the logs from",
                       default=config.editor,
                       choices=["etherpad", "stian_logs", "collab-react-components"])
cl_parser.add_argument("-t", "--texts", action="store_true",
                       help="Print the texts colored by ops and by author",
                       default=False)
cl_parser.add_argument("-viz", "--visualization",
                       action="store_true",
                       help="Display the visualization (proportion of participation of the users per pad/paragraph, "
                            "how synchronous they are...)",
                       default=False)
cl_parser.add_argument("-v", "--verbosity",
                       action="count",
                       default=0,
                       help="increase output verbosity (you can put -v or -vv)")
group = cl_parser.add_mutually_exclusive_group()
group.add_argument("--subset_of_pads",
                   help="Size of the subset of pads we will process",
                   default=None, type=int)
group.add_argument("--specific_pad",
                   help="Process only one pad",
                   default=None)
args = cl_parser.parse_args()

verbosity = args.verbosity
path_to_db = args.path_to_db
editor = args.editor
subset_of_pads = args.subset_of_pads
specific_pad = args.specific_pad
texts = args.texts
visualizations = args.visualization

if path_to_db is None and editor != 'collab-react-components':
    print("No arguments passed, displaying help and exiting:")
    cl_parser.print_help()
    cl_parser.exit()

list_of_elem_ops_per_pad = parser.get_elem_ops_per_pad_from_file(path_to_db, editor, specific_pad)

if subset_of_pads is not None:
    subset_of_keys = list(list_of_elem_ops_per_pad.keys())[:subset_of_pads]
    new_list_of_elem_ops_per_pad = dict()
    for key in subset_of_keys:
        new_list_of_elem_ops_per_pad[key] = list_of_elem_ops_per_pad[key]
    list_of_elem_ops_per_pad = new_list_of_elem_ops_per_pad

elif specific_pad is not None:
    list_of_elem_ops_per_pad = {specific_pad: list_of_elem_ops_per_pad[specific_pad]}

print("There are {} pads.".format(len(list_of_elem_ops_per_pad.keys())))
if verbosity == 1:
    print("The pads are", list(list_of_elem_ops_per_pad.keys()))

list_of_elem_ops_per_pad_sorted = operation_builder.sort_elem_ops_per_pad(list_of_elem_ops_per_pad)

pads = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad_sorted,
                                                        config.maximum_time_between_elem_ops)

for pad_name in pads:
    pad=pads[pad_name]
    # create the paragraphs
    pad.create_paragraphs_from_ops()
    # classify the operations of the pad
    pad.classify_operations(length_edit=config.length_edit,length_delete=config.length_delete)
    # find the context of the operation of the pad
    pad.build_operation_context(config.delay_sync, config.time_to_reset_day,config.time_to_reset_break)


for pad_name in pads:
    pad = pads[pad_name]
    if texts:
        print("PAD:", pad_name)
        text = pad.get_text()
        print("TEXT")
        print(text)

        print('\nCOLORED TEXT BY AUTHOR')
        pad.display_text_colored_by_authors()

        print('\nCOLORED TEXT BY OPS')
        pad.display_text_colored_by_ops()

    if visualizations:
        visualization.display_user_participation_paragraphs_with_del(pad)
        # plot the participation proportion per user per paragraphs
        #visualization.display_user_participation_paragraphs(pad)

        # plot the proportion of synchronous writing per paragraphs
        visualization.display_proportion_sync_in_paragraphs(pad)

        # plot the overall type counts
        visualization.display_overall_op_type(pad)

        # plot the counts of type per users
        visualization.display_types_per_user(pad)

        # Display user participation
        visualization.display_user_participation(pad)

    if verbosity > 1:
        # print('OPERATIONS')
        pad.display_operations()

        # print("PARAGRAPHS:")
        pad.display_paragraphs(verbose=1)
