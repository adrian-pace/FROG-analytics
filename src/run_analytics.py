from analytics import operation_builder, parser, visualization
import argparse
import config
import os
import traceback

def run(list_of_elem_ops_per_pad,
    verbosity=0,
    texts=False,
    texts_save_location=None,
    show_visualization=False,
    generate_csv=False,
    generate_csv_summary=False,
    figs_save_location=config.figs_save_location,
    maximum_time_between_elem_ops=config.maximum_time_between_elem_ops,
    length_edit=config.length_edit,
    length_delete=config.length_delete,
    delay_sync=config.delay_sync,
    time_to_reset_day=config.time_to_reset_day,
    time_to_reset_break=config.time_to_reset_break,
    print_pad_name=True,
    print_text=False,
    print_text_colored_by_authors=False,
    print_text_colored_by_ops=False,
    print_metrics_text=True):

    # Build the operations from the ElementaryOperation
    # (i.e. for each pad, create a Pad object containing the (non-elem) ops)
    pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(
        list_of_elem_ops_per_pad,
        maximum_time_between_elem_ops)

    separator_char = '\t' # For the csv files
    metric_names = ["user_participation_paragraph_score",
                    "prop_score",
                    "sync_score",
                    "alternating_score",
                    "break_score_day",
                    "break_score_short",
                    "type_overall_score_write",
                    "type_overall_score_paste",
                    "type_overall_score_delete",
                    "type_overall_score_edit",
                    "user_type_score_write",
                    "user_type_score_paste",
                    "user_type_score_delete",
                    "user_type_score_edit",
                    "added_chars",
                    "deleted_chars",
                    "paragraph_average_length",
                    "superparagraph_average_length",
                    "average_paragraphs_per_superparagraph",
                    "window_type_overall_score_write",
                    "window_type_overall_score_paste",
                    "window_type_overall_score_delete",
                    "window_type_overall_score_edit",
                    "window_user_type_score_write",
                    "window_user_type_score_paste",
                    "window_user_type_score_delete",
                    "window_user_type_score_edit"
                    ]

    if generate_csv:
        header = separator_char.join(["docID","author","posStart","posEnd",
                                      "timeStart","timeEnd","atomicOpCount",
                                      "type","textAdded","deletionLength",
                                      "paragraph","paragraphHistory","paragraphOriginal",
                                      "superparagraph",
                                      "proportionPad","proportionParagraph"])
        print(header)
    elif generate_csv_summary:
        header = separator_char.join(["docID"] + metric_names)
        print(header)

    # Create content for each Pad
    pad_id = 0 # This counter is used to generate IDs for the pads

    for pad_name, pad in pads.items():
        try:
            # create the paragraphs
            pad.create_paragraphs_from_ops(pad.get_elem_ops(True))
            # classify the operations of the pad
            pad.classify_operations(
                length_edit=length_edit,
                length_delete=length_delete
            )
            # find the context of the operation of the pad
            pad.build_operation_context(delay_sync,
                                        time_to_reset_day,
                                        time_to_reset_break)
            pad_id += 1

            if generate_csv:
                # Option 1: Use the name of the pad as the pad ID
                pad.display_csv(separator_char=separator_char)

                # Option 2: Use a custom string as the pad ID
                # pad.display_csv(separator_char=separator_char,
                #                 pad_id='id{}'.format(pad_id))

            elif generate_csv_summary:
                pad_metrics = pad.compute_metrics()
                pad_metrics_string = separator_char.join([
                    format(pad_metrics[metric]) for metric in metric_names])

                # Option 1: Use the name of the pad as the pad ID
                print(pad_name + separator_char + pad_metrics_string)

                # Option 2: Use a custom string as the pad ID
                # print('id{}'.format(pad_id) + separator_char + pad_metrics_string)

            else:
                # For each Pad, add the visualization
                if texts:
                    to_print = pad.to_print(
                        print_pad_name=print_pad_name,
                        print_text=print_text,
                        print_text_colored_by_authors=print_text_colored_by_authors,
                        print_text_colored_by_ops=print_text_colored_by_ops,
                        print_metrics_text=print_metrics_text)
                    if verbosity:
                        print("PRINT")
                        print(to_print)
                    if texts_save_location is not None:
                        if not os.path.isdir(texts_save_location):
                            os.makedirs(texts_save_location)
                        with open("{}/{}.txt".format(texts_save_location, pad_name),
                                  "w+",
                                  encoding="utf-8") as f:
                            f.write(to_print)

                if show_visualization:
                    # plot the participation proportion per user per paragraphs
                    visualization.display_user_participation(
                        pad,
                        figs_save_location)

                    visualization.display_user_participation_paragraphs(
                        pad,
                        figs_save_location)

                    visualization.display_user_participation_paragraphs_with_del(
                        pad,
                        figs_save_location)

                    # plot the proportion of synchronous writing per paragraphs
                    visualization.display_proportion_sync_in_paragraphs(
                        pad,
                        figs_save_location)

                    visualization.display_proportion_sync_in_pad(
                        pad,
                        figs_save_location)

                    # plot the overall type counts
                    visualization.display_overall_op_type(
                        pad,
                        figs_save_location)

                    # plot the counts of type per users
                    visualization.display_types_per_user(
                        pad,
                        figs_save_location)

                if verbosity > 1:
                    print("OPERATIONS")
                    pad.display_operations()

                    print("PARAGRAPHS:")
                    pad.display_paragraphs(verbose=1)

        except:
            print("Error at {}:".format(pad_name))
            print(traceback.format_exc())
            break


    if verbosity:
        print(
            "{} pad(s) contain a total of {} elementary operations".format(
                len(pads),
                sum(len(pad_elem_ops_treated) for
                    pad_elem_ops_treated in elem_ops_treated.values())
            )
        )


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
                                    "collab-react-components",
                                    "sql_dump"])

    cl_parser.add_argument("-t", "--texts", action="store_true",
                           help="Print the texts colored by ops and by author",
                           default=False)

    cl_parser.add_argument("--generate_csv", action="store_true",
                           help="Generate a csv file containing the information for all pads",
                           default=False)

    cl_parser.add_argument("--generate_csv_summary", action="store_true",
                           help="Generate a csv file containing the summarized information for all pads",
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

    if args.path_to_db is None and args.editor != "collab-react-components":
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
            list_of_elem_ops_per_pad = {key: list_of_elem_ops_per_pad[key]
                for key in subset_of_keys}
        elif args.specific_pad is not None:
            list_of_elem_ops_per_pad = {
                args.specific_pad: list_of_elem_ops_per_pad[args.specific_pad]
            }

        if args.verbosity:
            print("There are {} pads.".format(len(list_of_elem_ops_per_pad)))

            if args.verbosity > 1:
                print("The pads are ", list(list_of_elem_ops_per_pad.keys()))

        # Run the analysis
        run(list_of_elem_ops_per_pad,
            verbosity=args.verbosity,
            texts=args.texts,
            show_visualization=args.visualization,
            generate_csv=args.generate_csv,
            generate_csv_summary=args.generate_csv_summary)
