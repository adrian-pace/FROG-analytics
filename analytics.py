from analytics import operation_builder, parser, visualization
import argparse
import config

def run(list_of_elem_ops_per_pad, args):
    # Build the operations from the ElementaryOperation
    # (i.e. for each pad, create a Pad object containing the (non-elem) ops)
    pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(
        list_of_elem_ops_per_pad,
        config.maximum_time_between_elem_ops
    )

    # Create content for each Pad
    for pad_name in pads:
        pad = pads[pad_name]
        pad.create_content(pad.get_elem_ops(True),
                           config.length_edit,
                           config.length_delete,
                           config.delay_sync,
                           config.time_to_reset_day,
                           config.time_to_reset_break)

    if args.verbosity:
        print(
            "{} pad(s) contain a total of {} elementary operations".format(
                len(pads),
                sum(len(pad_elem_ops_treated) for
                    pad_elem_ops_treated in elem_ops_treated.values())
            )
        )

    # For each Pad, add the visualization
    for pad_name in pads:
        pad = pads[pad_name]
        if args.texts:
            print(pad.to_print(metrics_text=False))

        if args.visualization:
            visualization.display_user_participation_paragraphs_with_del(pad)

            # plot the participation proportion per user per paragraphs
            visualization.display_user_participation_paragraphs(pad)

            # plot the proportion of synchronous writing per paragraphs
            visualization.display_proportion_sync_in_paragraphs(pad)

            # plot the overall type counts
            visualization.display_overall_op_type(pad)

            # plot the counts of type per users
            visualization.display_types_per_user(pad)

            # Display user participation
            visualization.display_user_participation(pad)

        if args.verbosity > 1:
            # print('OPERATIONS')
            pad.display_operations()

            # print("PARAGRAPHS:")
            pad.display_paragraphs(verbose=1)


if __name__ == "__main__":
    # Parsing the command line arguments
    cl_parser = argparse.ArgumentParser(description="Run the analytics.")

    cl_parser.add_argument("-p", "--path_to_db",
                           help="Path to the database storing the edits",
                           default=None)

    cl_parser.add_argument("-e", "--editor",
                           help="Editor where the logs are from",
                           default=config.editor,
                           choices=["etherpad",
                                    "etherpadSQLite3",
                                    "stian_logs",
                                    "collab-react-components"])

    cl_parser.add_argument("-t", "--texts", action="store_true",
                           help="Print the texts colored by ops and by author",
                           default=False)

    cl_parser.add_argument("-viz", "--visualization",
                           action="store_true",
                           help="Display the visualization",
                           default=False)

    cl_parser.add_argument("-v", "--verbosity",
                           action="count",
                           default=0,
                           help="Increase output verbosity (either -v or -vv)")


    group = cl_parser.add_mutually_exclusive_group()

    group.add_argument("--subset_of_pads",
                       help="Size of the subset of pads to be processed",
                       default=None, type=int)

    group.add_argument("--specific_pad",
                       help="Specify the name of a single pad to be processed",
                       default=None)

    args = cl_parser.parse_args()

    if args.path_to_db is None and args.editor != 'collab-react-components':
        print("No arguments passed, displaying help and exiting:")
        cl_parser.print_help()
        cl_parser.exit()

    else:
        # Get a list of elementary operations for each pad
        list_of_elem_ops_per_pad = parser.get_elem_ops_per_pad_from_db(
            args.path_to_db,
            args.editor
        )

        # Keep only the pads we're interested in
        if args.subset_of_pads is not None:
            subset_of_keys = list(list_of_elem_ops_per_pad.keys())[:args.subset_of_pads]
            list_of_elem_ops_per_pad = {key: list_of_elem_ops_per_pad[key] for key in subset_of_keys}
        elif args.specific_pad is not None:
            list_of_elem_ops_per_pad = {args.specific_pad: list_of_elem_ops_per_pad[args.specific_pad]}

        if args.verbosity:
            print("There are {} pads.".format(len(list_of_elem_ops_per_pad)))

            if args.verbosity > 1:
                print("The pads are ", list(list_of_elem_ops_per_pad.keys()))

        # Run the analysis
        run(list_of_elem_ops_per_pad, args)
