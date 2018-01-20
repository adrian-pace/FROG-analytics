from analytics.Operations import ElementaryOperation, Paragraph, Operation
import numpy as np
import config


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

        self.authors = []
        """:type: list[str]"""

    def add_operation(self, operation):
        """
        Add an Operation to the list of ops

        :param operation: Operation to add
        """
        if not operation.pushed:
            operation.pushed = True
            self.operations.append(operation)

    def add_operations(self, operations):
        """
        Add a list of Operation to the list of ops

        :param operations: list of Operation to add
        """
        for op in operations:
            self.add_operation(op)

    def get_elem_ops(self, sorted_):
        """
        Get the list of ElementaryOperation from all the Operation. The result is ordered by timestamp. Good for
        building a representation of the text. Note that each ElementaryOperation know to which Operation it belongs

        :return: list of ElementaryOperation
        :rtype: list[ElementaryOperation]
        """
        # Recover all the elementary ops
        elem_ops = []
        for op in self.operations:
            for elem_op in op.elem_ops:
                elem_ops.append(elem_op)
        if sorted_:
            return ElementaryOperation.sort_elem_ops(elem_ops)
        else:
            return elem_ops

    def get_text(self, until_timestamp=None):
        """
        Return a string with the whole text

        :param until_timestamp:
        :return: the text written so far on the pad
        :rtype: str
        """
        elem_ops_ordered = self.get_elem_ops(sorted_=True)
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
        """

        letters = []
        letters_color = []
        idx_color = 0
        elem_ops_ordered = self.get_elem_ops(sorted_=True)
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
        string_colored = ''.join([color + letter for letter, color in zip(letters, letters_color)])

        # Change color back to original at the end and return
        return string_colored + get_colors()[0]

    def get_letters_and_colors_from_authors(self):
        """
        Create one list for all the letters representing the text and one list with the color of each letter according
        to its author.

        :return: list of letters representing the text and list of colors representing authors
        :rtype: list[str], list[str]
        """
        letters = []
        letters_color = []
        elem_ops_ordered = self.get_elem_ops(sorted_=True)
        authors = self.authors
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
        colored_text = ''.join([color + letter for letter, color in zip(letters, colors)])

        # Change color back to original
        return colored_text + get_colors()[0]

    def display_operations(self):
        """
        Print the descriptions of all the operations done on the pad
        """
        for op in self.operations:
            print(op)
            print()

    def create_paragraphs_from_ops(self, new_elem_ops_sorted):
        """
        Build the paragraphs for the pad based on the existing paragraphs and the new elementary operations
		
		:param new_elem_ops_sorted: list of elementary operation for the pad that we want to add to the paragraphs
        """

        def para_it_belongs(elem_op_to_look_for):
            """
            returns the index of the paragraph the elem_op should belong to. Returns -1 if it doesn't belong to any paragraph
            :param elem_op_to_look_for: elem op we are looking at
            :return: paragraph index
            """
            for para_i, paragraph in enumerate(self.paragraphs):
                if (not paragraph.new_line) \
                        and paragraph.abs_position \
                                <= elem_op_to_look_for.abs_position \
                                <= paragraph.abs_position + paragraph.get_length():
                    return para_i
            return -1

        # We will look at each elem_op and assign it to a new/existing paragraph
        for elem_op in new_elem_ops_sorted:
            # From where we will change the paragraph indices
            # should be infinity but this is enough since we can't add more than 2 paragraph
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
                    para.update_indices(elem_op)

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
                        #  are the first op considering merging), we might be merging with the paragraph just before.
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
                    merged_paragraph = Paragraph.merge(self.paragraphs[merge1], self.paragraphs[merge2], elem_op)
                    # We remove the second paragraph
                    del self.paragraphs[merge2]
                    # We put the merged paragraph where the first paragraph was
                    self.paragraphs[merge1] = merged_paragraph
                    # We will update the indices from the paragraph from here
                    update_indices_from = merge2

                # We need to notify the paragraphs that are after my edit, that their position might have changed
                for para in self.paragraphs[update_indices_from:]:
                    para.update_indices(elem_op)

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
                        while self.paragraphs[para_idx].abs_position \
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
                    para.update_indices(elem_op)

            # Assertions
            # TODO remove for production
            # Checking that the paragraph is in order
            assert self.paragraphs == sorted(self.paragraphs)
            # checking that length is not 0
            for i in range(0, len(self.paragraphs)):
                if self.paragraphs[i].length == 0:
                    print(self.pad_name, i, "\n", elem_op)
                    raise AssertionError
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

        # Find the  list of authors in the pad
        for op in self.operations:
            if op.author not in self.authors:
                self.authors.append(op.author)

    def display_paragraphs(self, verbose=0):
        """
        Print all the paragraphs contained in the pad

        :param verbose: print detailed info if verbose is 1
        :return:
        """
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

    def build_operation_context(self, delay_sync, time_to_reset_day, time_to_reset_break):
        """
        Build the context of each operation progressively added to the pad. The context is a dictionary containing
        whether a pad is synchronous wih an other author in the pad or in the paragraph and it contains list of
        authors accordingly.

        :param delay_sync: delay of synchronization between two authors
        :param time_to_reset_day: Number of milliseconds between two ops to indicate the first op of the day, by default
                8h
        :param time_to_reset_break: Number of milliseconds to indicate the first op after a break, by default 10min
        :return: None
        """
        # Iterate over all Operation of each Paragraph which is the same as to iterate all iterations of the pad
        pad_operations = self.operations
        len_pad = sum([abs(op.get_length_of_op()) for op in pad_operations])
        for op in pad_operations:
            # Initialize the context
            len_op = abs(op.get_length_of_op())
            op.context['proportion_pad'] = len_op / len_pad
            # An operation is originally 100% of a new paragraph
            op.context['proportion_paragraph'] = 1
            op.context['synchronous_in_pad'] = False
            op.context['synchronous_in_pad_with'] = []
            op.context['synchronous_in_paragraph'] = False
            op.context['synchronous_in_paragraph_with'] = []
            op.context['first_op_day'] = False
            op.context['first_op_break'] = False
            start_time = op.timestamp_start
            end_time = op.timestamp_end

            # Check in the pad if the other operations are written by someone else at the same time (+ some delay)
            op_index = 0
            for other_op in pad_operations:
                other_start_time = other_op.timestamp_start
                # Control if this is the current operation to do some processing on it
                if other_op == op:
                    # Check if the op is a first one
                    if op_index == 0 or other_start_time >= pad_operations[
                                op_index - 1].timestamp_end + time_to_reset_day:
                        op.context['first_op_day'] = True
                    elif op_index != 0 and other_start_time >= pad_operations[
                                op_index - 1].timestamp_end + time_to_reset_break:
                        op.context['first_op_break'] = True
                op_index += 1

                if other_op.author != op.author and other_op.author != 'Etherpad_admin' and op.author != 'Etherpad_admin' \
                        and end_time + delay_sync >= other_start_time >= start_time - delay_sync:
                    op.context['synchronous_in_pad'] = True
                    if other_op.author not in op.context['synchronous_in_pad_with']:
                        op.context['synchronous_in_pad_with'].append(other_op.author)
        for para in self.paragraphs:
            abs_length_para = 0
            para_ops = para.operations
            for op in para_ops:
                # Initialize the variables
                len_op = abs(op.get_length_of_op())
                start_time = op.timestamp_start
                end_time = op.timestamp_end

                # Compute the overall length of the paragraph
                abs_length_para += abs(op.get_length_of_op())

                for other_op in para_ops:
                    other_start_time = other_op.timestamp_start
                    if other_op.author != op.author and other_op.author != 'Etherpad_admin' and op.author != 'Etherpad_admin' \
                            and end_time + delay_sync >= other_start_time >= start_time - delay_sync:
                        op.context['synchronous_in_paragraph'] = True
                        if other_op.author not in op.context['synchronous_in_paragraph_with']:
                            op.context['synchronous_in_paragraph_with'].append(other_op.author)

                op.context['proportion_paragraph'] = len_op
            # Once we computed the absolute length of the paragraph, we compute the proportion (it is positive)
            for op in para_ops:
                if abs_length_para != 0:
                    op.context['proportion_paragraph'] /= abs_length_para
                else:
                    op.context['proportion_paragraph'] = 0

    def author_proportions(self, considerate_admin=True):
        """
        Compute the proportion of each authors for the entire pad.

        :param considerate_admin: Boolean to determine if we include the admin or not in our computations
        :return: the list of authors to consider and the resulting proportions in an array
        :rtype: list[str], np.array[float]
        """

        # Fetch all the authors who participated in the pad
        authors = self.authors

        # Delete the admin if needed
        if not considerate_admin and 'Etherpad_admin' in authors:
            authors = list(np.delete(authors, authors.index('Etherpad_admin')))
        # Initialize the number of letters written by each authors
        author_lengths = np.zeros(len(authors))
        # increment the participation accordingly
        for op in self.operations:
            op_author = op.author
            # Skip the incrementation if needed
            if considerate_admin or op_author != 'Etherpad_admin':
                author_lengths[authors.index(op_author)] += abs(op.get_length_of_op())

        # Compute the overall participation
        overall_length = sum(author_lengths)
        proportions = author_lengths / overall_length
        return authors, proportions

    @staticmethod
    def compute_entropy_prop(proportions, len_authors):
        """
        Compute the proportion score using the entropy and proportions.
        :param proportions: list of proportions summing up to 1
        :param len_authors: number of authors collaborating
        :return: the entropy score between 0 and 1. 0 is return if there are less than two authors
        """
        entropy_score = 0
        # Check that we have at least 2 authors different from the admin
        if len_authors >= 2:
            # Change zero values to small values to note divide by zero
            proportions = np.array([0.000001 if prop == 0 else prop for prop in proportions])
            # Compute the entropy with the proportions
            entropy_score = sum(np.log(1 / proportions) * proportions) / np.log(len_authors)
        return entropy_score

    def prop_score(self):
        """
        Compute the proportion score using the entropy.

        :return: proportion score between 0 and 1
        :rtype: float
        """
        authors, proportions = self.author_proportions(considerate_admin=False)
        return self.compute_entropy_prop(proportions, len(authors))

    def sync_score(self):
        """
        Compute the synchronous and asynchronous scores.

        :return: synchronous and asynchronous scores, floats between 0 and 1.
        :rtype: (float,float)
        """
        prop_sync = 0
        prop_async = 0
        len_pad_no_admin = sum(
            [abs(op.get_length_of_op()) if op.author != 'Etherpad_admin' else 0 for op in self.operations])
        for op in self.operations:
            if op.context['synchronous_in_pad']:
                prop_sync += abs(op.get_length_of_op())/len_pad_no_admin
            elif op.author != 'Etherpad_admin':
                prop_async += abs(op.get_length_of_op())/len_pad_no_admin
        return prop_sync, prop_async

    def prop_paragraphs(self):
        """
        Compute the proportion of each paragraphs.

        :return: list with the paragraphs names, list with the proportions for each authors for each paragraphs.
        :rtype: list[str], list[dict(str: float)]
        """
        # Init variables
        author_names = self.authors
        prop_authors_paragraphs = []
        paragraph_names = []
        i = 1
        for paragraph in self.paragraphs:
            # Initialize a dictionary containing participation proportion for each authors
            prop_authors = {author_name: 0 for author_name in author_names}
            # Only take into account the real paragraphs (not the new lines)
            if not paragraph.new_line:
                # Create the label of the paragraph
                paragraph_names.append('p' + str(i))
                i += 1
                for op in paragraph.operations:
                    prop_authors[op.author] += abs(op.context[
                                                       'proportion_paragraph'])  # increment with the corresponding prop
                prop_authors_paragraphs.append(prop_authors)
        return paragraph_names, prop_authors_paragraphs

    def alternating_score(self):
        """
        Compute the alternating score that is the number of main author alternations between paragraphs divided by the
        total number of alternations of paragraphs.

        :return: the alternating score which is a float between 0 and 1. Return 0 if there is less than 2 paragraph
        """
        num_alt = 0
        main_authors = []

        # Compute the proportions for each paragraphs for each authors
        _, prop_authors_paragraphs = self.prop_paragraphs()
        for para in prop_authors_paragraphs:
            # Add the author who participated the most in the paragraph
            main_authors.append(max(para.keys(), key=(lambda key: para[key])))

        # Increment the alternation counter only when we change authors
        for i, author in enumerate(main_authors):
            if i > 0 and author != main_authors[i - 1]:
                num_alt += 1
        # Divide the overall counter of alternations by the maximum number of alternations
        if len(main_authors) > 1:
            return num_alt / (len(main_authors) - 1)
        # If there is only one paragraph, there is no alternation: we return score null
        else:
            return 0

    def user_participation_paragraph_score(self):
        """
        Compute the score of user participation per paragraph.

        :return: Score between 0 and 1 being the weighted average (paragraph lengths) of the proportion entropy of users
        """
        paragraph_participations = []
        _, prop_authors_paragraphs = self.prop_paragraphs()
        paragraph_lengths = []

        # Get the length of each paragraphs
        for para in self.paragraphs:
            if not para.new_line:
                paragraph_lengths.append(para.get_abs_length())

        # Compute the entropy of author proportions for each paragraphs
        for para in prop_authors_paragraphs:
            author_props = list(para.values())
            paragraph_participations.append(self.compute_entropy_prop(author_props, len(author_props)))

        # Compute the weighted average according to paragraph lengths
        overall_score = sum(np.multiply(paragraph_participations, paragraph_lengths))
        if sum(paragraph_lengths) != 0:
            return overall_score / sum(paragraph_lengths)
        else:
            # If no paragraph, we choose to return a score of zero
            return 0

    def break_score(self, break_type):
        """
        Compute the breaking score, i.e. the score that tells whether a pad is written only in one time or with
        multiple accesses.

        :param break_type: string that is either 'short' for short breaks or 'day' for daily ones.
        :return: The score is the number of breaks over the whole pad divided by the time spent on the pad. Between 0
        and 1.
        """
        # Compute the time spent in s
        operations = Operation.sort_ops(self.operations)
        first_timestamp = operations[0].timestamp_start
        last_timestamp = operations[len(operations) - 1].timestamp_end
        time_spent = (last_timestamp - first_timestamp) / 1000  # in s

        # Compute the number of breaks according to the type
        num_break = 0
        for op in self.operations:
            if break_type == 'short':
                if op.context['first_op_break']:
                    num_break += 1
            elif break_type == 'day':
                if op.context['first_op_day']:
                    num_break += 1
        # Calculate the final score
        if time_spent >= 1:
            return num_break / time_spent
        else:
            # If less than 1s is spent on the pad, the score is zero
            return 0

    def type_overall_score(self, op_type):
        """
        Compute proportion of one type: write, delete, edit or paste over the whole pad.

        :param op_type: the operation type 'write', 'delete', 'edit' or 'paste'.
        :return: the proportion of the operation type
        """
        type_count = 0
        op_count = 0
        # Count the number of operations
        for op in self.operations:
            if op.type != 'jump':
                op_count += 1
                if op.type == op_type:
                    type_count += 1

        # Calculate the overall proportion
        return type_count / op_count

    def user_type_score(self, op_type):
        """
        Compute the entropy for an operation type on all users except the admin. It creates a matrix of dimension
        (num_user x num_types) counting the number of different operations per user. It normalizes the counts according
        to the rows and then normalize the proportions according to the columns to compute a valid entropy for each
        entropy.

        :param op_type: string being the operation type 'write', 'delete', 'edit', 'paste'.
        :return:the entropy score for one type over all users.
        """
        types = ['write', 'edit', 'delete', 'paste']
        users = self.authors[:]
        # Remove the admin
        if 'Etherpad_admin' in users: users.remove('Etherpad_admin')
        count_type = np.zeros((len(users), len(types)))
        for op in self.operations:
            if op.type != 'jump' and op.author != 'Etherpad_admin':
                user_idx = users.index(op.author)
                type_idx = types.index(op.type)
                count_type[user_idx, type_idx] += 1
        # Normalize the counter of op types per user
        total_type = count_type.sum(axis=1)[:, None]
        norm_type = np.divide(count_type, total_type, out=np.zeros_like(count_type), where=total_type != 0)

        # Normalize the proportion of users per types
        total_user = norm_type.sum(axis=0)
        norm_user = np.divide(norm_type, total_user, out=np.zeros_like(norm_type), where=total_user != 0)

        # Compute the entropy for all types
        type_scores = []
        for type_props in norm_user.T:
            type_scores.append(self.compute_entropy_prop(type_props, len(users)))
        return type_scores[types.index(op_type)]

