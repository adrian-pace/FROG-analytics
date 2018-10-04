import sqlite3
import config
from analytics.Operations import ElementaryOperation
import csv
import ast
from pymongo import MongoClient

MONGODB_PORT = None


def parse_op_collab_react(op_array, editor):
    """
    Parse a op in OT type into a list of elementary operations.
    There will be missing the author, timestamp...
    https://github.com/ottypes/text


    :param editor: FROG or collab-react-components
    :param op_array: string to parse
    :return : List of elem_ops contained in op
    :rtype: list[ElementaryOperation]
    :type op_array: [{'p': list[int], str: str}]
    """

    elem_ops = []
    """:type: list[ElementaryOperation]"""
    for op in op_array:
        if editor == 'collab-react-components':
            assert len(op['p']) == 1
            position = op['p'][0]  # Collab
        else:
            if len(op['p']) != 2:
                raise AssertionError("len(op['p']) != 2. Might be because you"
                    "are treating ill-formatted logs from the DB.")
            assert op['p'][0] == 'text'
            position = op['p'][1]  # FROG

        if 'sd' in op.keys():
            # Deleting some letters
            length_to_delete = len(op['sd'])
            elem_ops.append(ElementaryOperation(
                operation_type="del",
                abs_position=position,
                length_to_delete=length_to_delete,
                changeset=op)
            )
        if 'si' in op.keys():
            # Inserting some letters
            text_to_add = op['si']
            elem_ops.append(ElementaryOperation(
                operation_type="add",
                abs_position=position,
                text_to_add=text_to_add,
                changeset=op)
            )

    return elem_ops


def parse_changeset_etherpad(changeset):
    """
    Parse a changeset of type etherpad into a list of elementary operations.
    There will be missing the author,
    timestamp... http://policypad.readthedocs.io/en/latest/changesets.html

    :param changeset: string to parse
    :type changeset: str

    :return : List of elem_ops contained in the changeset
    :rtype: list[ElementaryOperation]

    """

    def find_next_symbol_idx(string, start):
        """ Find the next symbol from start """
        symbols = ['|', '$', '+', '-', '=', '*']
        for i in range(start, len(string)):
            if string[i] in symbols:
                return i
        else:
            # We reached the end of the text
            return len(string)

    line_number = 0
    line_abs_position = 0
    position = 0
    position_inline = 0
    elementary_operations = []
    used_databank = 0

    # Finding the first operations. It's always a |
    idx = find_next_symbol_idx(changeset, 0)

    while idx < len(changeset):
        if changeset[idx] == '|':
            # It's going to be taken care of by elif changeset[idx].isalnum()
            idx += 1

        elif changeset[idx] == '$':
            # Should have already been added with the '+'
            return elementary_operations

        elif changeset[idx].isalnum():
            # Format is |L+N,|L-N or |L=N
            symbol_idx = find_next_symbol_idx(changeset, idx)

            if changeset[symbol_idx] == '=':
                # |L=N
                # Keep N characters from source text, containing L newlines.
                # The last character kept MUST be a newline, and the final
                # newline of the document is allowed.
                # L
                line_number += int(changeset[idx:symbol_idx], 36)
                next_symbol_position = find_next_symbol_idx(changeset,
                                                            symbol_idx + 1)
                # N
                line_abs_position += int(changeset[symbol_idx + 1:next_symbol_position], 36)
                position += int(changeset[symbol_idx + 1:next_symbol_position], 36)
                idx = next_symbol_position

            elif changeset[symbol_idx] == '+':
                # |L+N
                # Insert N characters from the source text, containing L newlines.
                # The last character inserted MUST be a newline, but not the (new)
                # document's final newline.

                next_symbol_position = find_next_symbol_idx(changeset, symbol_idx + 1)
                # We care about  N (size of the addition) since we will date N chars from the databank.
                # noinspection PyPep8Naming
                N = int(changeset[symbol_idx + 1:next_symbol_position], 36)
                data_bank = changeset[changeset.find('$') + 1:]
                text_to_add = data_bank[used_databank:used_databank + N]
                elementary_operations.append(ElementaryOperation(
                    "add",
                    position,
                    text_to_add=text_to_add,
                    line_number=line_number,
                    position_inline=position_inline,
                    changeset=changeset)
                )
                used_databank += N
                position += N
                idx = next_symbol_position

            else:
                assert (changeset[symbol_idx] == '-')

                # |L-N
                # Delete N characters from the source text, containing L newlines.
                # The last character inserted MUST be a newline, but not the (old)
                # document's final newline.
                next_symbol_position = find_next_symbol_idx(changeset, symbol_idx + 1)
                # N
                chars_to_delete = int(changeset[symbol_idx + 1:next_symbol_position], 36)
                idx = next_symbol_position
                elementary_operations.append(ElementaryOperation(
                    "del",
                    position,
                    length_to_delete=chars_to_delete,
                    line_number=line_number,
                    position_inline=position_inline,
                    changeset=changeset)
                )

        elif changeset[idx] == '=':
            # Keep N characters from the source text, none of them newlines
            # (position inline)
            next_symbol_position = find_next_symbol_idx(changeset, idx + 1)
            # We add the inline offset
            position += int(changeset[idx + 1:next_symbol_position], 36)
            position_inline += int(changeset[idx + 1:next_symbol_position], 36)
            idx = next_symbol_position

        elif changeset[idx] == '+':
            next_symbol_position = find_next_symbol_idx(changeset, idx + 1)
            # We care about N (size of the addition). We only take N chars from the databank (not counting the
            # already used ones)
            N = int(changeset[idx + 1:next_symbol_position], 36)
            data_bank = changeset[changeset.find('$') + 1:]
            text_to_add = data_bank[used_databank:used_databank + N]
            elementary_operations.append(ElementaryOperation(
                "add",
                position,
                text_to_add=text_to_add,
                line_number=line_number,
                position_inline=position_inline,
                changeset=changeset)
            )
            used_databank += N
            position += N
            idx = next_symbol_position

        elif changeset[idx] == '-':
            # Remove the next n symbols
            next_symbol_position = find_next_symbol_idx(changeset, idx + 1)
            chars_to_delete = int(changeset[idx + 1:next_symbol_position], 36)
            idx = next_symbol_position
            elementary_operations.append(ElementaryOperation(
                "del",
                position,
                length_to_delete=chars_to_delete,
                line_number=line_number,
                position_inline=position_inline,
                changeset=changeset)
            )

        else:
            # TODO: Format with '*'
            assert changeset[idx] == '*'
            idx = find_next_symbol_idx(changeset, idx + 1)


def extract_elem_ops_etherpad(line_dict, timestamp_offset, editor):
    """
	extract the ElementaryOperation from a line in etherpad format

	:param line_dict: line we want to extrat the ElementaryOperation from
	:param timestamp_offset: offset we want to add to the timestamps.
        This is because sometimes we generate multiple elementary operations
        from a single line and we want to keep their order by changing a
        little bit the timestamp of the elem_op. This change is repercuted
        on all the following ElementaryOperation.
	:param editor: name of editor
	:return: the list of ElementaryOperation
	"""
    # Retrieve name of pad
    pad_name_idx = line_dict['key'].find("pad:") + len("pad:")
    pad_name_end_idx = line_dict['key'].find(':revs:', pad_name_idx)
    pad_name = line_dict['key'][pad_name_idx:pad_name_end_idx]

    revs = int(line_dict['key'][pad_name_end_idx + len('revs:') + 1:])
    changeset = line_dict['val']['changeset']
    author_name = line_dict['val']['meta']['author']
    timestamp = line_dict['val']['meta']['timestamp']

    elem_ops = parse_changeset_etherpad(changeset)
    elem_ops_result = []
    for elem_op in elem_ops:
        if author_name == '':
            # if it's the line generated automatically by etherpad
            elem_op.author = 'Etherpad_admin'
        else:
            elem_op.author = author_name
        elem_op.timestamp = timestamp + timestamp_offset
        timestamp_offset += 1
        elem_op.revs = revs
        elem_op.pad_name = pad_name
        elem_op.editor = editor

        elem_ops_result.append(elem_op)
    return pad_name, elem_ops_result, timestamp_offset


def get_elem_ops_per_pad_from_db(path_to_db, editor, index_from_lines=0, revs_mongo=None, regex=None):
    """
    Get the list of ElementaryOperation parsed from the db file

    :param path_to_db: path to the db file containing the operations
    :param editor: 'etherpad' or 'collab-react-components' or 'stian_logs'
        or 'etherpadSQLite3' or 'FROG'
    :param index_from_lines:
    :return: list of ElementaryOperation
    :rtype: dict[str,list[ElementaryOperation]]
    """
    # TODO: add the selective parsing
    list_of_elem_ops_per_pad = dict()

    if editor == 'etherpad':
        # TODO: add the sorted algorithm

        with open(path_to_db) as f:
            lines = f.readlines()
        # Sometimes, we will get multiple elem_ops when we parse the changeset
        # We need to give them different timestamps. So we add an offset to
        # the timestamp of each elem_op to differentiate them. We keep track
        # of this offset to apply it to the following ops
        timestamp_offset = 0
        for line in lines[index_from_lines:]:
            # We look at relevant log lines
            if '{"key":"pad:' in line:
                line_changed = line.replace("false", "False").replace("null", "None")
                line_dict = dict(eval(line_changed))
                if 'revs' in line_dict['key']:
                    pad_name, elem_ops, timestamp_offset = extract_elem_ops_etherpad(
                        line_dict,
                        timestamp_offset,
                        editor
                    )
                    if pad_name not in list_of_elem_ops_per_pad.keys():
                        list_of_elem_ops_per_pad[pad_name] = []
                    list_of_elem_ops_per_pad[pad_name] += elem_ops

    elif editor == 'etherpadSQLite3':
        # TODO: add the sorted algorithm

        # Connect to the db file.
        conn = sqlite3.connect(path_to_db)
        c = conn.cursor()
        c.execute("SELECT * FROM store;")
        # Fetch all the entries.
        entries = c.fetchall()
        conn.close()
        timestamp_offset = 0
        # For each entry, parse it and extract the elem_op
        for entry in entries[index_from_lines:]:
            if "pad:" in entry[0] and "revs" in entry[0]:
                data = eval(entry[1].replace("false", "False").replace("null", "None"))
                line_dict = {'key': entry[0], 'val': data}

                pad_name, elem_ops, timestamp_offset = extract_elem_ops_etherpad(line_dict,
                                                                                 timestamp_offset,
                                                                                 editor)
                if pad_name not in list_of_elem_ops_per_pad.keys():
                    list_of_elem_ops_per_pad[pad_name] = []
                list_of_elem_ops_per_pad[pad_name] += elem_ops

    elif editor == 'collab-react-components' or editor == 'FROG':
        # Connect to the DB
        client = MongoClient(port=config.mongodb_port)
        db = client[config.mongodb_database_name]
        o_docs = db[config.mongodb_collection_name]

        # If we have revs_mongo, that mean we will look for the editor ops
        # whose revs is after the revs specified in revs_mongo
        if revs_mongo is not None and len(revs_mongo) != 0:
            list_or = []
            for pad_name in revs_mongo:
                # Fetching only the new operations.
                # (Whose revs is after revs_mongo[pad_name])
                list_or.append({'d': pad_name, 'v': {'$gt': revs_mongo[pad_name]}})
            if regex:
                # If a regex is specified, keep listening also for new pads
                # that are not in revs_mongo but match the regex
                list_or.append({'$and': [
                    {'d': {'$regex': regex}},
                    {'d': {'$not': {'$in': list(revs_mongo.keys())}}}]})
            query = {'$or': list_or}
        else:
            if regex:
                # Fetch all the documents that match the regex
                query = {'d': {'$regex': regex}}
            else:
                # Fetch everything
                query = {}
            revs_mongo = dict()

        print(query)
        # For each operation we find, we parse it and create the ElementaryOperation
        o_docs_find = o_docs.find(query)
        for item in o_docs_find:
            print(item)
            # Parsing
            if 'create' not in item.keys():
                pad_name = item['d']
                timestamp = item['m']['ts']
                op = item['op']
                revs = item['v']
                author_name = item['src']
                elem_ops = parse_op_collab_react(op, editor)
                for elem_op in elem_ops:
                    elem_op.author = author_name
                    elem_op.timestamp = timestamp
                    elem_op.revs = revs
                    elem_op.pad_name = pad_name
                    elem_op.editor = editor

                    if not (pad_name in list_of_elem_ops_per_pad.keys()):
                        list_of_elem_ops_per_pad[pad_name] = [elem_op]
                    else:
                        list_of_elem_ops_per_pad[pad_name].append(elem_op)

        client.close()
        # Shouldn't be necessary
        for pad_name in list_of_elem_ops_per_pad:
            list_of_elem_ops_per_pad[pad_name] = sorted(list_of_elem_ops_per_pad[pad_name],
                                                        key=(lambda x: x.timestamp))
            revs_mongo[pad_name] = max(map((lambda x: x.revs),
                                            list_of_elem_ops_per_pad[pad_name]))

        # TODO remove Assertions for release
        for pad_name in list_of_elem_ops_per_pad:
            assert list_of_elem_ops_per_pad[pad_name] == sorted(list_of_elem_ops_per_pad[pad_name],
                                                                key=(lambda x: x.timestamp))
        return list_of_elem_ops_per_pad, revs_mongo

    elif editor == 'stian_logs':
        sorted_lines = []
        with open(path_to_db, encoding="utf8") as f:
            lines = csv.DictReader(f)
            # We need them sorted
            for line_dict in lines:
                # We look at relevant log lines
                if 'pad:' in line_dict['key']:
                    line_dict['value'] = line_dict['value'].replace("false",
                        "False").replace("null", "None")
                    if 'revs' in line_dict['key']:
                        val_dict = ast.literal_eval(line_dict['value'])
                        timestamp = val_dict['meta']['timestamp']
                        sorted_lines.append((int(timestamp), line_dict))
            sorted_lines = sorted(sorted_lines, key=lambda tup: tup[0])

            # Sometimes, we will get multiple elem_ops when we parse the
            # changeset. We need to give them different timestamps.
            # So we add an offset to the timestamp of each elem_op to
            # differentiate them. We keep track of this offset to apply it to
            # the following ops
            timestamp_offset = 0
            list_of_elem_ops_per_pad = dict()

            for timestamp, line_dict in sorted_lines[index_from_lines:]:
                # TODO check if we can do just eval ()
                val_dict = ast.literal_eval(line_dict['value'])
                pad_name_idx = line_dict['key'].find("pad:") + len("pad:")
                pad_name_end_idx = line_dict['key'].find(':revs:', pad_name_idx)
                pad_name = line_dict['key'][pad_name_idx:pad_name_end_idx]
                revs = int(line_dict['key'][pad_name_end_idx + len('revs:') + 1:])

                changeset = val_dict['changeset']

                author_name = val_dict['meta']['author']
                if not (pad_name in list_of_elem_ops_per_pad.keys()):
                    list_of_elem_ops_per_pad[pad_name] = []

                elem_ops = parse_changeset_etherpad(changeset)
                for elem_op in elem_ops:
                    if author_name == '':
                        # if it's the line generated automatically by etherpad
                        elem_op.author = 'Etherpad_admin'
                    else:
                        elem_op.author = author_name
                    elem_op.timestamp = timestamp + timestamp_offset
                    timestamp_offset += 1
                    elem_op.revs = revs
                    elem_op.pad_name = pad_name

                    list_of_elem_ops_per_pad[pad_name].append(elem_op)

    else:
        raise ValueError("Undefined editor")

    # TODO remove Assertions for release
    for pad_name in list_of_elem_ops_per_pad:
        assert list_of_elem_ops_per_pad[pad_name] == sorted(list_of_elem_ops_per_pad[pad_name],
                                                            key=(lambda x: x.timestamp))

    return list_of_elem_ops_per_pad
