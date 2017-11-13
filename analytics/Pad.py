from analytics.Operations import ElementaryOperation, Paragraph, Operation


def get_colors():
    colors = []
    for i in range(30, 38):
        colors.append('\033[' + str(i) + 'm')
    for i in range(90, 97):
        colors.append('\033[' + str(i) + 'm')
    return colors


class Pad:
    """
    Pad. Contains all the operations for a particular pad.
    """

    def __init__(self, pad_name):
        """
        Create a pad

        :param pad_name:  name of the new pad
        """

        self.paragraphs = []
        """:type: list[Paragraph]"""

        self.pad_name = pad_name

        self.operations = []
        """:type: list[Operation]"""

    def add_operation(self, operation):
        """
        Add an Operation to the list of ops

        :param operation: Operation to add
        """
        self.operations.append(operation)

    def add_operations(self, operations):
        """
        Add a list of Operation to the list of ops

        :param operations: list of Operation to add
        """
        for op in operations:
            self.add_operation(op)

    def get_all_elementary_operation(self):
        """
        get all the elementary operation of the pad

        :return: the list of elem_ops
        :rtype: list[ElementaryOperation]
        """
        elem_ops = []
        for op in self.operations:
            for elem_op in op.elem_ops:
                elem_ops.append(elem_op)
        return elem_ops

    def get_elem_ops_ordered(self):
        """
        Get the list of ElementaryOperation from all the Operation. The result is ordered by timestamp. Good for
        building a representation of the text. Note that each ElementaryOperation know to which Operation it belongs

        :return: list of ElementaryOperation
        :rtype: list[ElementaryOperation]
        """
        # Recover all the elementary ops
        elem_ops_list = self.get_all_elementary_operation()
        return ElementaryOperation.sort_elem_ops(elem_ops_list)

    def get_authors(self):
        """
        Get the list of authors who participated in the pad.

        :return: list of authors
        :rtype: list[str]
        """
        authors = []
        for op in self.operations:
            if op.author not in authors:
                authors.append(op.author)
        return list(authors)

    def get_text(self, until_timestamp=None):
        """
        Return a string with the whole text

        :param until_timestamp:
        :return: the text written so far on the pad
        :rtype: str
        """
        elem_ops_ordered = self.get_elem_ops_ordered()
        text = ""
        for elem_id, elem_op in enumerate(elem_ops_ordered):
            if until_timestamp is not None and elem_op.timestamp > until_timestamp:
                return text
            if elem_op.operation_type == 'add':
                # We add to the end of the ext
                if '*' in elem_op.text_to_add or '*' in text or len(elem_ops_ordered) - 1 == elem_id:
                    pass
                if len(text) == elem_op.abs_position:
                    text += elem_op.text_to_add
                else:
                    text = text[:elem_op.abs_position] + elem_op.text_to_add + text[elem_op.abs_position:]
            elif elem_op.operation_type == 'del':
                text = text[:elem_op.abs_position] + text[elem_op.abs_position + elem_op.length_to_delete:]
            else:
                raise AttributeError("Undefined elementary operation")
        return text

    def display_text_colored_by_ops(self):
        """
        Print the colored text according to the operations.

        :return: None
        """

        letters = []
        letters_color = []
        idx_color = 0
        elem_ops_ordered = self.get_elem_ops_ordered()
        op_to_color = {}
        colors = get_colors()
        for idx, elem_op in enumerate(elem_ops_ordered):
            idx_elem = elem_op.abs_position
            if elem_op.operation_type == 'add':
                # We find the right color to print
                op = elem_op.belong_to_operation
                if op in op_to_color:
                    color = op_to_color[op]
                else:
                    op_to_color[op] = colors[idx_color % len(colors)]
                    idx_color += 1
                    color = op_to_color[op]

                # We add to the end of the ext
                if idx_elem == len(letters):
                    letters += list(elem_op.text_to_add)
                    letters_color += [color] * elem_op.get_length_of_op()
                else:
                    letters = letters[:idx_elem] + list(elem_op.text_to_add) + letters[idx_elem:]
                    letters_color = letters_color[:idx_elem] + [color] * elem_op.get_length_of_op() + letters_color[
                                                                                                      idx_elem:]
            elif elem_op.operation_type == 'del':
                letters = letters[:idx_elem] + letters[idx_elem + elem_op.length_to_delete:]
                letters_color = letters_color[:idx_elem] + letters_color[idx_elem + elem_op.length_to_delete:]
            else:
                raise AttributeError("Undefined elementary operation")
        # Print letter after letter with the right color
        print(''.join([color + letter for letter, color in zip(letters, letters_color)]))

        # Change color back to original
        print(colors[0])

    def get_letters_and_colors_from_authors(self):
        """
        Create one list for all the letters representing the text and one list with the color of each letter according
        to its author.

        :return: list of letters representing the text and list of colors representing authors
        :rtype: list[str], list[str]
        """
        letters = []
        letters_color = []
        elem_ops_ordered = self.get_elem_ops_ordered()
        authors = self.get_authors()
        colors = get_colors()
        for elem_op in elem_ops_ordered:
            idx_elem = elem_op.abs_position
            color = colors[authors.index(elem_op.author) % len(colors)]
            if elem_op.operation_type == 'add':
                # We add to the end of the ext
                if idx_elem == len(letters):
                    letters += list(elem_op.text_to_add)
                    letters_color += [color] * elem_op.get_length_of_op()
                else:
                    letters = letters[:idx_elem] + list(elem_op.text_to_add) + letters[idx_elem:]
                    letters_color = letters_color[:idx_elem] + [color] * elem_op.get_length_of_op() + letters_color[
                                                                                                      idx_elem:]
            elif elem_op.operation_type == 'del':
                letters = letters[:idx_elem] + letters[idx_elem + elem_op.length_to_delete:]
                letters_color = letters_color[:idx_elem] + letters_color[idx_elem + elem_op.length_to_delete:]
            else:
                raise AttributeError("Undefined elementary operation")
        return letters, letters_color

    def display_text_colored_by_authors(self):
        """
        Display the text the same way as get_text but with different colors according to authors.

        :return: None
        """
        letters, colors = self.get_letters_and_colors_from_authors()

        # Print letter after letter with the right color
        print(''.join([color + letter for letter, color in zip(letters, colors)]))

        # Change color back to original
        print(colors[0])

    def display_operations(self):
        """
        Print the descriptions of all the operations done on the pad

        :return: None
        """
        for op in self.operations:
            print(op)
            print()

    def create_paragraphs_from_ops(self):
        """
        Build the paragraphs for the pad

        """

        def para_it_belongs(elem_op_to_look_for):
            """
            returns the index of the paragraph the elem_op should belong to
            :param elem_op_to_look_for:
            :return:
            """
            for para_i, paragraph in enumerate(self.paragraphs):
                if (not paragraph.new_line) \
                    and paragraph.abs_position \
                        <= elem_op_to_look_for.abs_position \
                        <= paragraph.abs_position + paragraph.get_length():
                    return para_i
            return -1

        print(self.pad_name)

        # We will look at each elem_op and assign it to a new/existing paragraph
        for elem_op in self.get_elem_ops_ordered():

            # From where we will change the paragraph indices
            # should be infity but this is enough since we can't add more than 2 paragraph
            update_indices_from = len(self.paragraphs) + 3

            # If it is a new line, we will create a new paragraph and insert it at the right place
            if elem_op.operation_type == "add" and "\n" in elem_op.text_to_add:
                # To which paragraph this op corresponds ?
                para_it_belongs_to = para_it_belongs(elem_op)

                # If it is supposed to be in a paragraph which is a new line or at the end of paragraph
                if para_it_belongs_to == -1:

                    # Is it an op at the beginning ?
                    if elem_op.abs_position == 0:
                        self.paragraphs.insert(0, Paragraph(elem_op, new_line=True))
                        update_indices_from = 1

                    # Is it the last op ?
                    elif self.paragraphs[len(self.paragraphs) - 1].abs_position \
                            + self.paragraphs[len(self.paragraphs) - 1].length \
                            <= elem_op.abs_position:
                        self.paragraphs.append(Paragraph(elem_op, new_line=True))

                    # Find where we should insert it
                    else:
                        para_idx = 0
                        while self.paragraphs[para_idx].abs_position \
                                + self.paragraphs[para_idx].length \
                                < elem_op.abs_position:
                            para_idx += 1
                        # Insert it
                        self.paragraphs.insert(para_idx + 1, Paragraph(elem_op, new_line=True))
                        update_indices_from = para_idx + 2

                # or if it is at the start of a non-newline para:
                elif self.paragraphs[para_it_belongs_to].abs_position == elem_op.abs_position:
                    self.paragraphs.insert(para_it_belongs_to, Paragraph(elem_op, new_line=True))
                    update_indices_from = para_it_belongs_to + 1

                # or if it is at the end of a non-newline para:
                elif self.paragraphs[para_it_belongs_to].abs_position \
                        + self.paragraphs[para_it_belongs_to].length \
                        == elem_op.abs_position:
                    self.paragraphs.insert(para_it_belongs_to + 1, Paragraph(elem_op, new_line=True))
                    update_indices_from = para_it_belongs_to + 2

                # We will split the paragraph in two, where there is the newline
                else:
                    # The two paragrpahs from the split
                    para1, para2 = Paragraph.split(self.paragraphs[para_it_belongs_to], elem_op.abs_position)

                    # We delete the old paragraph
                    del self.paragraphs[para_it_belongs_to]

                    # since we add a new line
                    para2.abs_position += 1

                    # Insert the second paragraph
                    self.paragraphs.insert(para_it_belongs_to, para2)
                    # Insert the new line just before
                    self.paragraphs.insert(para_it_belongs_to, Paragraph(elem_op, new_line=True))
                    # Insert the first paragraph
                    self.paragraphs.insert(para_it_belongs_to, para1)
                    # From where we will update the indices
                    update_indices_from = para_it_belongs_to + 3

                # We need to notify the paragraphs that are after my edit, that their position might have changed
                for para in self.paragraphs[update_indices_from:]:
                    para.abs_position += elem_op.get_length_of_op()

            # If it is a deletion
            elif elem_op.operation_type == "del":
                # For all paragraph add the elem_op if it affects them partly or delete them if it affects them
                # totally It is also possible that we have to merge the paragraph on the extremities if no new_lines
                # are in between
                # Index of the left paragraph to merge
                merge1 = None
                # Index of the right paragraph to merge
                merge2 = None
                # Paragraphs to remove
                to_remove = []
                # We will check for each paragraph if they are concerned
                for para_idx, para in enumerate(self.paragraphs):

                    # We are deleting only this paragraph
                    if elem_op.abs_position == para.abs_position \
                            and elem_op.abs_position + elem_op.length_to_delete \
                                == para.abs_position + para.get_length():
                        # Add to the list to remove
                        to_remove.append(para_idx)
                        # We will update the indices from here
                        update_indices_from = para_idx + 1

                        # If the paragraph just before is not a new line, we might merge it with the one after
                        if 0 < para_idx \
                                and para.new_line \
                                and (not self.paragraphs[para_idx - 1].new_line) \
                                and merge1 is None:
                            # Paragraph just before which will merge if there is a merge
                            merge1 = para_idx - 1

                        # if the paragraph just after is not a new line and we are merging (merge1 is not None -> the
                        #  paragraph before was not a new line), then we will merge
                        if para_idx < len(self.paragraphs) - 1 \
                                and merge1 is not None \
                                and (not self.paragraphs[para_idx + 1].new_line):
                            # Paragraph just after which will merge with the paragraph at merge1
                            merge2 = para_idx + 1

                        # Since we delete only this paragraph, we can't break
                        break

                    # paragraph is fully contained in deletion and it touches other paragraphs
                    elif elem_op.abs_position \
                            <= para.abs_position \
                            and elem_op.abs_position + elem_op.length_to_delete \
                                >= para.abs_position + para.get_length():
                        # We remove the whole paragraph
                        to_remove.append(para_idx)
                        # shouldn't be necessary since it will be taken care by the last paragraph we delete.
                        update_indices_from = para_idx + 1

                        # If we are a new line and before us was text and we are currently not merging (this means we
                        #  are the first op considering merging), we might be merging with the paragraph jsut before.
                        # This is usually when the current paragraph is the start of the deletion
                        if 0 < para_idx \
                                and para.new_line \
                                and (not self.paragraphs[para_idx - 1].new_line) \
                                and merge1 is None:
                            # The paragraph just before that might merge
                            merge1 = para_idx - 1

                        # if we are considering merging and the paragraph just after is not a new line, then it might
                        #  be the second part of the merge
                        if para_idx < len(self.paragraphs) - 1 \
                                and merge1 is not None \
                                and (not self.paragraphs[para_idx + 1].new_line):
                            # The paragraph just after that we might merge with
                            merge2 = para_idx + 1
                        else:
                            # If the paragraph just after is not a possible merger. Then reset the right en of the merge
                            merge2 = None

                    # Start of deletion is within our para whether the  end is within para or not
                    elif para.abs_position \
                            <= elem_op.abs_position \
                            < para.abs_position + para.get_length():
                        # Add the operation to the para
                        para.add_elem_op(elem_op)
                        # update the indices from here
                        update_indices_from = para_idx + 1
                        # If there is a merge, it will be from here
                        merge1 = para_idx

                    # End of deletion is within our para but start isn't (or it would have gone in the elif before
                    elif para.abs_position \
                            < elem_op.abs_position + elem_op.length_to_delete \
                            <= para.abs_position + para.get_length():
                        # If there is no merge, we apply the op to the paragraph. Otherwise, it is included in the
                        # first merge
                        if merge1 is None:
                            # Add the elem_op
                            para.add_elem_op(elem_op)
                            # Update the indices from here
                            update_indices_from = para_idx + 1
                        # We will merge with this paragraph (if there is a merge, aka. merge1 is not None)
                        merge2 = para_idx

                    # paragraph is not concerned
                    else:
                        pass

                # Check that if the start of the deletion is withing a para and the end of the deletion is within
                # another para. If so we merge the two paragraphs.
                if (merge1 is not None) and (merge2 is not None) and not (merge1 in to_remove or merge2 in to_remove):
                    # Merged paragraph
                    merged_paragraph = Paragraph.merge(self.paragraphs[merge1], self.paragraphs[merge2])
                    # We modify the length of the second part of the merge since its start is deleted
                    self.paragraphs[merge2].length -= elem_op.abs_position \
                                                      + elem_op.length_to_delete \
                                                      - self.paragraphs[merge2].abs_position

                    # We remove the second paragraph
                    del self.paragraphs[merge2]
                    # We put the merged paragraph where the first paragraph was
                    self.paragraphs[merge1] = merged_paragraph
                    # We will update the indices from the paragraph from here
                    update_indices_from = merge2

                # We need to notify the paragraphs that are after my edit, that their position might have changed
                for para in self.paragraphs[update_indices_from:]:
                    para.abs_position += elem_op.get_length_of_op()

                # Remove the paragraphs we are supposed to remove
                for idx in to_remove[::-1]:
                    del self.paragraphs[idx]

            # Keep our paragraphs as they are, just add the elem_op
            else:
                # Find the paragraph it should belong to
                para_it_belongs_to = para_it_belongs(elem_op)

                # If we should create a new para for this elem_op
                if para_it_belongs_to == -1:
                    # The new paragraph
                    new_paragraph = Paragraph(elem_op)

                    # If we are at the start of the document
                    if elem_op.abs_position == 0:
                        self.paragraphs.insert(0, new_paragraph)
                        update_indices_from = 1

                    # If we are at the end of the paragraph
                    elif self.paragraphs[len(self.paragraphs) - 1].abs_position \
                            + self.paragraphs[len(self.paragraphs) - 1].length \
                            <= elem_op.abs_position:
                        self.paragraphs.append(new_paragraph)

                    # Insert the new paragraph in the good place
                    else:
                        # Look where we should insert it
                        para_idx = 0
                        while self.paragraphs[para_idx].abs_position\
                                + self.paragraphs[para_idx].length \
                                < elem_op.abs_position:
                            para_idx += 1
                        # Insert it
                        self.paragraphs.insert(para_idx + 1, new_paragraph)
                        # Update indices of the next paragraphs from here
                        update_indices_from = para_idx + 2

                # Just add to the paragraph
                else:
                    # Add it
                    self.paragraphs[para_it_belongs_to].add_elem_op(elem_op)
                    # Update indices of the next paragraphs from here
                    update_indices_from = para_it_belongs_to + 1

                # We need to notify the paragraphs that are after my edit, that their position might have changed
                for para in self.paragraphs[update_indices_from:]:
                    para.abs_position += elem_op.get_length_of_op()

            # Assertions
            # TODO remove for production
            # Checking that the paragraph is in order
            assert self.paragraphs == sorted(self.paragraphs)
            # Checking that the paragraphs touch each others
            for i in range(1, len(self.paragraphs)):
                if self.paragraphs[i - 1].abs_position \
                        + self.paragraphs[i - 1].length \
                        != self.paragraphs[i].abs_position:
                    print(elem_op)
                    raise AssertionError
            # Checking that a text paragraph is encapsulated between two new_line paragraphs
            for i in range(1, len(self.paragraphs) - 1):
                if not self.paragraphs[i].new_line \
                        and (not self.paragraphs[i + 1].new_line or not self.paragraphs[i + 1].new_line):
                    print(elem_op)
                    raise AssertionError

    def display_paragraphs(self, verbose=0):
        for para in self.paragraphs:
            print(para.__str__(verbose))
            print("\n")

    def classify_operations(self, length_edit, length_delete):
        """
        Classify all the operations types from the pad. The different types are Write, Edit, Delete, Copy/Paste or Jump.

        :param length_edit: Threshold in length to differentiate a Write type from an Edit or an Edit from a Deletion.
        :param length_delete:  Threshold in length to consider the op as a deletion
        :return: None
        """
        for op in self.operations:
            # Classify the type according to the length of the operation
            len_op = op.get_length_of_op()
            if len_op >= length_edit:
                if len(op.elem_ops) == 1:
                    op.type = 'paste'
                else:
                    op.type = 'write'
            elif len_op <= -length_delete:
                op.type = 'delete'
            elif len(op.elem_ops) == 1 \
                    and op.elem_ops[0].operation_type == "add" \
                    and op.elem_ops[0].text_to_add == '\n':
                op.type = 'jump'
            else:
                op.type = 'edit'
