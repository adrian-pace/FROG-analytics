# Main file to display metrics and visualization from the etherpad
# dirty database
from analytics.parser import get_elem_ops_per_pad_from_db
import config
import run_analytics

path_to_db = "/home/lucia/program_files/etherpad-lite/var/dirty.db"

# We get all the elementary operation from the db.
list_of_elem_ops_per_pad = get_elem_ops_per_pad_from_db(
    path_to_db=path_to_db,
    editor='etherpad'
)

run_analytics.run(list_of_elem_ops_per_pad,
    texts=True,
    texts_save_location=None,
    show_visualization=True,
    figs_save_location=config.figs_save_location,
    print_pad_name=True,
    print_text=True,
    print_text_colored_by_authors=False,
    print_text_colored_by_ops=False,
    print_metrics_text=True,
    verbosity=1
    )