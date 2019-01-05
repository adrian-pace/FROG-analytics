path_to_db = "etherpad/var/dirty.db"  # Path to database
editor = "etherpad"  # Style of the database
maximum_time_between_elem_ops = 20000  # milliseconds
delay_sync = 180000  # delay to differentiate if two ops are in sync in ms (3min)
time_to_reset_day = int(288e5)  # time to reinitialize the first op of the day (8h)
time_to_reset_break = 600000  # time to reset first op after a break (10min)
length_edit = 15  # Threshold in length to differentiate a Write type from an Edit or an edit from a Deletion.
length_delete = 15  # Threshold in length to consider the op as a deletion
figs_save_location = "../figures"
texts_save_location = "../texts"

# Mongo configuration
# mongodb_port = None
# mongodb_database_name = "my-collaborative-app"
# mongodb_collection_name = "o_collab_data_documents"
mongodb_port = 30000
mongodb_database_name = "sharedb"
mongodb_collection_name = "o_rz"

# To which url should the program send its metrics updates
update_post_url = "http://35.229.83.91:5000/"
# How many seconds should you wait before treating the new elementary operations. (recommended to be less than
# maximum_time_between_elem_ops)
server_update_delay = 1
# How often you send the metrics to the server
send_update_delay = 5
# Maximum length for paragraph/superparagraph ids
max_len_id = 30

default_lines = [
            "Welcome to your Task Pad!  Use this pad to write your answer:",
            "1) You and your partners need to reach consensus when you're finished and all click 'Submit'.",
            "2) Avoid chatting in this space.  Use the chat for that!",
            "3) Remember, we're looking for a report of the best supported claims.",
            "4) Use the evidence you have (you'll need to decide how much to read) to create a summary for the minister.",
            "5) Use boldface font to create headings.",
            "6) You can insert URLs for references, or use in-line citations like this: (Templaar, 2014).",
            "Good luck!",
            "Welcome to Etherpad!",
            "This pad text is synchronized as you type, so that everyone viewing this page sees the same text. This allows you to collaborate seamlessly on documents!",
            "Get involved with Etherpad at http://etherpad.org"
        ]