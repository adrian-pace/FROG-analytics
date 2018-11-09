# Main file to display the metrics and visualizations from the belgian
# experiment pads
from analytics.parser import get_elem_ops_per_pad_from_db
import config
import run_analytics
import os

list_of_elem_ops_per_pad = dict()
elemOpsCounter = 0
root_of_dbs = "../Data/belgian_experiment/"
# Walk among all the files containing the pads.
for (dirpath, dirnames, filenames) in os.walk(root_of_dbs):
    for filename in filenames:
        if ".db" in filename:
            path_to_db = os.path.join(dirpath, filename)
            # Fetching the new operations
            list_of_elem_ops_per_main = get_elem_ops_per_pad_from_db(
                path_to_db=path_to_db,
                editor='etherpadSQLite3'
            )
            # the pad extracted from each file always have the same name so we
            # give them a new name based on their path
            pad_name = path_to_db[len(root_of_dbs):path_to_db.find("data") - 1]
            # We check that there is only one pad per file as there should be
            # (one pad per session)
            assert len(list_of_elem_ops_per_main.keys()) == 1
            # we rename it
            list_of_elem_ops_per_pad[pad_name] = list_of_elem_ops_per_main['main']

run_analytics.run(list_of_elem_ops_per_pad,
    texts=True,
    texts_save_location=config.texts_save_location,
    show_visualization=True,
    figs_save_location=config.figs_save_location,
    print_pad_name=True,
    print_text=True,
    print_text_colored_by_authors=True,
    print_text_colored_by_ops=True,
    print_metrics_text=True)
