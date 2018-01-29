path_to_db = "etherpad/var/dirty.db"  # Path to database
editor = 'etherpad'  # Style of the database
maximum_time_between_elem_ops = 20000  # milliseconds
delay_sync = 180000  # delay to differentiate if two ops are in sync in ms (3min)
time_to_reset_day = int(288e5)  # time to reinitialize the first op of the day (8h)
time_to_reset_break = 600000  # time to reset first op after a break (10min)
length_edit = 15  # Threshold in length to differentiate a Write type from an Edit or an edit from a Deletion.
length_delete = 15  # Threshold in length to consider the op as a deletion
figs_save_location = './figures'

# Mongo configuration
# mongodb_port = None
# mongodb_database_name = 'my-collaborative-app'
# mongodb_collection_name = 'o_collab_data_documents'
mongodb_port = 30000
mongodb_database_name = 'sharedb'
mongodb_collection_name = 'o_rz'

# To which url should the program send its metrics updates
update_post_url = 'http://35.229.83.91:5000/'
# How many seconds should you wait before treating the new elementary operations. (recommended to be less than
# maximum_time_between_elem_ops)
server_update_delay = 1
# How often you send the metrics to the server
send_update_delay = 5
