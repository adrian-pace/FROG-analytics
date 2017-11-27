from analytics.Operations import ElementaryOperation
import csv
import ast


def parse_changeset_etherpad(changeset):
    """
    Parse a changeset of type etherpad into a list of elementary operations. There will be missing the author, timestamp...
    http://policypad.readthedocs.io/en/latest/changesets.html

    :param changeset: string to parse
    :type changeset: str

    :return : List of elem_ops contained in the changeset
    :rtype: list[ElementaryOperation]

    """

    def find_next_symbol_idx(string, start):
        """
        Find the next symbol from start
        """
        symbols = ['|', '$', '+', '-', '=', '*']
        for i in range(start, len(string)):
            if string[i] in symbols:
                return i
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
                # Keep N characters from the source text, containing L newlines.
                # The last character kept MUST be a newline, and the final newline
                # of the document is allowed.
                # L
                line_number += int(changeset[idx:symbol_idx], 36)
                next_symbol_position = find_next_symbol_idx(changeset, symbol_idx + 1)
                # N
                line_abs_position += int(changeset[symbol_idx + 1:next_symbol_position], 36)
                position += int(changeset[symbol_idx + 1:next_symbol_position], 36)
                idx = next_symbol_position
            elif changeset[symbol_idx] == '+':
                # |L+N
                # Insert N characters from the source text, containing L newlines.
                # The last character inserted MUST be a newline, but not the (new)
                # document’s final newline.

                next_symbol_position = find_next_symbol_idx(changeset, symbol_idx + 1)
                # We care about  N (size of the addition) since we will date N chars from the databank.
                N = int(changeset[symbol_idx + 1:next_symbol_position], 36)
                data_bank = changeset[changeset.find('$') + 1:]
                text_to_add = data_bank[used_databank:used_databank + N]
                elementary_operations.append(ElementaryOperation("add",
                                                                 position,
                                                                 text_to_add=text_to_add,
                                                                 line_number=line_number,
                                                                 position_inline=position_inline,
                                                                 changeset=changeset))
                used_databank += N
                position += N
                idx = next_symbol_position
            else:
                assert (changeset[symbol_idx] == '-')

                # |L-N
                # Delete N characters from the source text, containing L newlines.
                # The last character inserted MUST be a newline, but not the (old)
                # document’s final newline.
                next_symbol_position = find_next_symbol_idx(changeset, symbol_idx + 1)
                # N
                chars_to_delete = int(changeset[symbol_idx + 1:next_symbol_position], 36)
                idx = next_symbol_position
                elementary_operations.append(ElementaryOperation("del",
                                                                 position,
                                                                 length_to_delete=chars_to_delete,
                                                                 line_number=line_number,
                                                                 position_inline=position_inline,
                                                                 changeset=changeset))
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
            # We care about N (size of the addition). We only take N chars from the databank (not counting the already used ones)
            N = int(changeset[idx + 1:next_symbol_position], 36)
            data_bank = changeset[changeset.find('$') + 1:]
            text_to_add = data_bank[used_databank:used_databank + N]
            elementary_operations.append(ElementaryOperation("add",
                                                             position,
                                                             text_to_add=text_to_add,
                                                             line_number=line_number,
                                                             position_inline=position_inline,
                                                             changeset=changeset))
            used_databank += N
            position += N
            idx = next_symbol_position

        elif changeset[idx] == '-':
            # Remove the next n symbols
            next_symbol_position = find_next_symbol_idx(changeset, idx + 1)
            chars_to_delete = int(changeset[idx + 1:next_symbol_position], 36)
            idx = next_symbol_position
            elementary_operations.append(ElementaryOperation("del",
                                                             position,
                                                             length_to_delete=chars_to_delete,
                                                             line_number=line_number,
                                                             position_inline=position_inline,
                                                             changeset=changeset))
        else:
            # TODO: Format with '*'
            assert changeset[idx] == '*'
            idx = find_next_symbol_idx(changeset, idx + 1)


def parse_op_collab_react(op_array):
    """
    Parse a op in OT type into a list of elementary operations . There will be missing the author, timestamp...
    https://github.com/ottypes/text

   
    :param op_array: string to parse
    :return : List of elem_ops contained in op
    :rtype: list[ElementaryOperation]
    :type op_array: [{'p': list[int], str: str}]
    """

    elem_ops = []
    """:type: list[ElementaryOperation]"""
    for op in op_array:
        assert len(op['p']) == 1
        position = op['p'][0]
        if 'si' in op.keys():
            # Inserting some letters
            text_to_add = op['si']
            elem_ops.append(ElementaryOperation(operation_type="add",
                                                abs_position=position,
                                                text_to_add=text_to_add,
                                                changeset=op))
        if 'sd' in op.keys():
            # Deleting some letters
            length_to_delete = len(op['sd'])
            elem_ops.append(ElementaryOperation(operation_type="del",
                                                abs_position=position,
                                                length_to_delete=length_to_delete,
                                                changeset=op))
    return elem_ops


def get_elem_ops_per_pad_from_file(path_to_db,editor,pad_name):
    if editor=='stian_logs':
        return get_elem_ops_per_pad_from_ether_csv(path_to_db,pad_name)
    else:
        return get_elem_ops_per_pad_from_db(path_to_db,editor,pad_name)

def get_elem_ops_per_pad_from_db(path_to_db=None, editor=None, pad_name=None):
    """
    Get the list of ElementaryOperation parsed from the db file

    :param pad_name:
    :param editor: 'etherpad' or 'collab-react-components'
    :param path_to_db: path to the db file containing the operations
    :return: list of ElementaryOperation
    :rtype: dict[str,list[ElementaryOperation]]
    """
    # todo add the selective parsing
    list_of_elem_ops_per_pad = dict()

    if editor == 'etherpad':
        #todo add the sorted algorithm here too
        with open(path_to_db) as f:
            lines = f.readlines()
        # Sometimes, we will get multiple elem_ops when we parse the changeset. We need to give them different
        # timestamps. So we add an offset to the timestamp of each elem_op to differentiate them. We keep track of this
        # offset to apply it to the following ops
        timestamp_offset = 0
        for line in lines:
            # We look at relevant log lines
            if '{"key":"pad:' in line:
                line_changed = line.replace("false", "False").replace("null", "None")
                line_dict = dict(eval(line_changed))
                if 'revs' in line_dict['key']:
                    pad_name_idx = line_dict['key'].find("pad:") + len("pad:")
                    pad_name_end_idx = line_dict['key'].find(':revs:', pad_name_idx)
                    pad_name = line_dict['key'][pad_name_idx:pad_name_end_idx]
                    revs = int(line_dict['key'][pad_name_end_idx + len('revs:') + 1:])
                    changeset = line_dict['val']['changeset']
                    author_name = line_dict['val']['meta']['author']
                    timestamp = line_dict['val']['meta']['timestamp']
                    if not (pad_name in list_of_elem_ops_per_pad.keys()):
                        list_of_elem_ops_per_pad[pad_name] = []

                    elem_ops = parse_changeset_etherpad(changeset)
                    for i, elem_op in enumerate(elem_ops):
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

                        list_of_elem_ops_per_pad[pad_name].append(elem_op)

    elif editor == 'collab-react-components':
        from pymongo import MongoClient
        client = MongoClient()
        db = client['my-collaborative-app']
        o_docs = db['o_collab_data_documents']
        for item in o_docs.find():
            if 'create' not in item.keys():
                pad_name = item['d']
                timestamp = item['m']['ts']
                op = item['op']
                revs = item['v']
                author_name = item['src']
                elem_ops = parse_op_collab_react(op)
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

    else:
        raise ValueError("Undefined editor")

    return list_of_elem_ops_per_pad

def get_elem_ops_per_pad_from_ether_csv(path_to_csv, pad_name=None):
    """
    Get the list of ElementaryOperation parsed from the etherpad csv file

    :param path_to_csv: path to the db file containing the operations
    :return: list of ElementaryOperation
    :rtype: dict[str,list[ElementaryOperation]]
    """
    sorted_lines = []
    with open(path_to_csv, encoding="utf8") as f:
        lines = csv.DictReader(f)
        # We need them sorted
        for i, line_dict in enumerate(lines):
            # We look at relevant log lines
            if (pad_name is not None and 'pad:'+pad_name in line_dict['key']) \
                    or (pad_name is None and 'pad:' in line_dict['key']):
                line_dict['value'] = line_dict['value'].replace("false", "False").replace("null", "None")
                if 'revs' in line_dict['key']:
                    val_dict = ast.literal_eval(line_dict['value'])
                    timestamp = val_dict['meta']['timestamp']
                    sorted_lines.append((int(timestamp),line_dict))
    sorted_lines=sorted(sorted_lines, key=lambda tup: tup[0])

    # Sometimes, we will get multiple elem_ops when we parse the changeset. We need to give them different
    # timestamps. So we add an offset to the timestamp of each elem_op to differentiate them. We keep track of this
    # offset to apply it to the following ops
    timestamp_offset=0
    list_of_elem_ops_per_pad = dict()

    for timestamp,line_dict in sorted_lines:
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
        for i, elem_op in enumerate(elem_ops):
            if author_name == '':
                # if it's the line generated automatically by etherpad
                elem_op.author = 'Etherpad_admin'
            else:
                elem_op.author = author_name
            elem_op.timestamp = timestamp + timestamp_offset
            timestamp_offset+=1
            elem_op.revs = revs
            elem_op.pad_name = pad_name

            list_of_elem_ops_per_pad[pad_name].append(elem_op)

    return list_of_elem_ops_per_pad
