from analytics import Operations
from analytics.Operations import ElementaryOperation, Operation
from analytics.Pad import Pad


def build_operations_from_elem_ops(
    list_of_elem_ops_per_pad,
    maximum_time_between_elem_ops,
    dic_author_current_operations_per_pad=None,
    pads=None):
    """
    Create a object Pad for each pad and create the operations for each one.
    If pads is specified, add the new operation to the current list of pads.
    If dic_author_current_operations_per_pad is not None, it represents the
    last operation of each author in case the new elementary operation should
    be added to this operation instead of creating a new operation.

    :param list_of_elem_ops_per_pad: dictionary of elementary operation per pad
    :type list_of_elem_ops_per_pad: dict[str,list[ElementaryOperation]]
    :param maximum_time_between_elem_ops: maximum type idle so that it's part
        of the same op
    :type maximum_time_between_elem_ops: int
    :param dic_author_current_operations_per_pad: The current ongoing operations
    :type dic_author_current_operations_per_pad: dict[str,dict[str,Operation]]
    :param pads: The current pads
    :type pads: dict[str,Pad]
    :return: a dictionary of pads, the current operations that might changed
        depending on the next elem_ops, and the list of elem_ops (they might
        have changed if there were some new lines.
    :rtype: (dict[str,Pad],
             dict[str,dict[str,Operation]],
             dict[str,list[ElementaryOperation]])
    """


    # The new list of elementary operations since it might change (if we have
    # new lines, we isolate the new line for the construction of the paragraphs)
    elem_ops_treated_per_pad = dict()
    """:type: dict[str,list[ElementaryOperation]]"""

    for pad_name in list_of_elem_ops_per_pad:
        # For current pad_name, retrieve the pad.
        # If it doesn't exist, create a new pad
        if pads is not None:
            if pad_name in pads:
                pad = pads[pad_name]
            else:
                pad = Pad(pad_name)
        else:
            pads = dict()
            """:type:dict[str,Pad]"""
            pad = Pad(pad_name)

        # If we have operations in standby, we get them.
        if dic_author_current_operations_per_pad is not None:
            if pad_name in dic_author_current_operations_per_pad:
                dic_author_current_operations = dic_author_current_operations_per_pad[pad_name]
            else:
                dic_author_current_operations = dict()
                """:type:dict[str,Operation]"""
        else:
            dic_author_current_operations_per_pad = dict()
            """:type:dict[str,dict[str,Operation]]"""
            dic_author_current_operations = dict()
            """:type:dict[str,Operation]"""
        elem_ops_treated_per_pad[pad_name] = []

        # For each elementary operation, we study it and add it to a existing
        # operation or create a new one
        for elem_op in list_of_elem_ops_per_pad[pad_name]:
            if elem_op.operation_type == "add" and "\n" in elem_op.text_to_add:
                # Split the elem_op if it contains a new line
                idx_newline = elem_op.text_to_add.find("\n")
                elem_op_txts = []
                # Text before the newline
                if elem_op.text_to_add[0] != "\n":
                    first_elem_op_txt = elem_op.text_to_add[:idx_newline]
                else:
                    first_elem_op_txt = ""

                # we decomposed the op by their new_line
                while idx_newline != -1:
                    elem_op_txts.append("\n")
                    # Add the text between our new line and the next new line
                    idx_next_newline = elem_op.text_to_add.find(
                        "\n", idx_newline + 1)
                    if idx_next_newline == -1:
                        # We are the last new line
                        # We add the remaining chars (if there are none,
                        # it will be an empty string)
                        last_elem_op_txt = elem_op.text_to_add[idx_newline + 1:]

                    elif (elem_op.text_to_add[idx_newline:idx_next_newline] !=
                        "\n"):
                        # if the text in between is also characters
                        elem_op_txts.append(elem_op.text_to_add[
                            idx_newline + 1:elem_op.text_to_add.find(
                                "\n", idx_newline + 1
                            )
                        ])
                    # Update our position
                    idx_newline = idx_next_newline

                abs_position = elem_op.abs_position
                # For the first element we add it to the current operation
                # if possible
                if first_elem_op_txt != "":
                    first_elem_op = elem_op.copy()
                    first_elem_op.text_to_add = first_elem_op_txt
                    elem_ops_treated_per_pad[pad_name].append(first_elem_op)
                    dic_author_current_operations = treat_op(
                        first_elem_op,
                        dic_author_current_operations,
                        pad,
                        maximum_time_between_elem_ops
                    )
                    abs_position += len(first_elem_op.text_to_add)
                # push to the pad the op because after we only have new lines
                if elem_op.author in dic_author_current_operations.keys():
                    pad.add_operation(dic_author_current_operations[elem_op.author])
                    del dic_author_current_operations[elem_op.author]
                # For all the new lines and text after we create
                #separate elem_ops

                # +10 just to be safe
                number_of_new_elem_ops = float(len(elem_op_txts)) + 10
                for idx, txt in enumerate(elem_op_txts):
                    if txt is not "":
                        # Warning ! doesn't update the line number
                        new_elem = elem_op.copy()
                        new_elem.text_to_add = txt
                        new_elem.abs_position = abs_position
                        new_elem.current_position = abs_position
                        # We offset the timestamp so that we keep the order
                        new_elem.timestamp += (idx + 1) / number_of_new_elem_ops
                        elem_ops_treated_per_pad[pad_name].append(new_elem)
                        pad.add_operation(Operation(new_elem))
                        abs_position += len(new_elem.text_to_add)

                if last_elem_op_txt != "":
                    last_elem_op = elem_op.copy()
                    last_elem_op.text_to_add = last_elem_op_txt
                    last_elem_op.abs_position = abs_position
                    last_elem_op.current_position = abs_position
                    # We offset the timestamp so that we keep the order
                    last_elem_op.timestamp += ((len(elem_op_txts) + 1) /
                        number_of_new_elem_ops)
                    elem_ops_treated_per_pad[pad_name].append(last_elem_op)
                    dic_author_current_operations[elem_op.author] = Operation(
                        last_elem_op
                    )

            else:
                # if the elementary operation does not contain a new line
                elem_ops_treated_per_pad[pad_name].append(elem_op)
                dic_author_current_operations = treat_op(
                    elem_op,
                    dic_author_current_operations,
                    pad,
                    maximum_time_between_elem_ops
                )

            # Notify all other current operation of other users that their
            # indices might have changed (important to check when a user has
            # moved the text)
            for user in dic_author_current_operations.keys():
                if user is not elem_op.author:
                    dic_author_current_operations[user].update_indices(elem_op)

        # at the end of the list of elementary operations, push all the unfinished
        # operations to the pad (we might add it new elementary operation later on)
        for remaining_authors in dic_author_current_operations:
            pad.add_operation(dic_author_current_operations[remaining_authors])

        # Keep track of the the last operations to which we could maybe add
        # the next elementary operations
        pad.operations.sort(key=pad.operationSort)
        pads[pad_name] = pad
        dic_author_current_operations_per_pad[pad_name] = dic_author_current_operations

    return pads, dic_author_current_operations_per_pad, elem_ops_treated_per_pad


def treat_op(elem_op,
    dic_author_current_operations,
    pad,
    maximum_time_between_elem_ops):
    """
    Treat the elementary operation by adding it to the current operation or
    creating one and adding the last to the pad, depending on the criterias

    :param elem_op: The elem_op to add
    :type elem_op: ElementaryOperation
    :param dic_author_current_operations: The list of current ongoing
        operations by authors
    :type dic_author_current_operations: dict[str,Operation]
    :param pad: The pad we look at
    :type pad: Pad
    :param maximum_time_between_elem_ops: Maximum type idle so that it's
        part of the same op
    :type maximum_time_between_elem_ops: int
    :return: The updated dic_dic_author_current_operations
    :rtype: dict[str,Operation]
    """
    if elem_op.author in dic_author_current_operations.keys():
        # This author is already in a current Operation
        new_time = elem_op.timestamp
        new_position = elem_op.abs_position
        current_op = dic_author_current_operations[elem_op.author]

        # check whether it should be part of the current operation
        if new_time - current_op.timestamp_end < maximum_time_between_elem_ops:
            # Time between the last ElementaryOperation of the Operation and
            # our current ElementaryOperation is smaller than
            # maximum_time_between_elem_ops
            if (current_op.position_start_of_op -
                abs(elem_op.get_length_of_op()) <=
                new_position <=
                current_op.position_start_of_op +
                abs(current_op.get_length_of_op())):
                # Checking that the position of the elementary op is more or
                # less inside the Operation bounds
                current_op.add_elem_op(elem_op)
                return dic_author_current_operations

            else:
                # If it shouldn't be added to the operation. We push the
                # operation and create a new operation
                pad.add_operation(current_op)
                dic_author_current_operations[elem_op.author] = Operation(elem_op)
                return dic_author_current_operations
        else:
            # If it shouldn't be added to the operation. We push the
            # operation and create a new operation
            pad.add_operation(current_op)
            dic_author_current_operations[elem_op.author] = Operation(elem_op)
            return dic_author_current_operations
    else:
        # New OP for this author
        dic_author_current_operations[elem_op.author] = Operation(elem_op)
        return dic_author_current_operations


def sort_elem_ops_per_pad(list_of_elem_ops_per_pad):
    """
    sort a list of ElementaryOperation based on the timestamp

    :param list_of_elem_ops_per_pad: list of ElementaryOperation to sort
    :type list_of_elem_ops_per_pad: dict[str,list[ElementaryOperation]]
    :return: sorted list of ElementaryOperation by their timestamp
    :rtype: dict[str,list[ElementaryOperation]]
    """

    list_of_elem_ops_per_pad_sorted = {
        pad_name: Operations.ElementaryOperation.sort_elem_ops(elem_ops)
        for pad_name, elem_ops in list_of_elem_ops_per_pad.items()
    }

    return list_of_elem_ops_per_pad_sorted
