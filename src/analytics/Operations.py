import config
import random
import string

class ElementaryOperation:
    """
    Elementary operation (finest granularity). Such as addition or removal of
    one letter or a very short sequence.

    - operation_type: "add" or "del"
    - abs_position: position in document
    - length_to_delete: how many characters we should remove if the op is
        "del" from the position of the op. Not taken into account otherwise
    - text_to_add: Text to add if th eop is "add". Not taken into account
        otherwise.
    - line_number: line number not necessary since we have the position
    - position_inline: position in the current line. Not necessary since
        we have the position
    - author
    - timestamp
    - pad name
    - revs: version number
    - changeset: Original information encoded in Etherpad format
        (http://policypad.readthedocs.io/en/latest/changesets.html)
    - belong_to_operation : to which operation it belongs
    """

    def __init__(
        self,
        operation_type, abs_position,
        length_to_delete=None,
        text_to_add=None,
        line_number=None,
        position_inline=None,
        author='Default',
        timestamp=None,
        pad_name=None,
        revs=None,
        changeset=None,
        editor=None,
        belong_to_operation=None):
        """
        Elementary operation (finest granularity). Such as addition or removal
        of one letter or a very short sequence.

        :param operation_type: "add" or "del"
        :type operation_type: str
        :param abs_position: position in document
        :type abs_position: int
        :param length_to_delete: how many characters we should remove if the
            op is "del" from the position of the op. Not taken into account
            otherwise
        :type length_to_delete: int
        :param text_to_add: Text to add if th eop is "add". Not taken into
            account otherwise.
        :type text_to_add: str
        :param line_number: line number not necessary since we have the position
        :type line_number: int
        :param position_inline: position in the current line. Not necessary
            since we have the position
        :type position_inline: int
        :param author: author
        :type author: str
        :param timestamp: time of the edit
        :type timestamp: float
        :param pad_name: pad name
        :type pad_name: str
        :param revs: version number
        :param changeset: Original information encoded in Etherpad format
            (http://policypad.readthedocs.io/en/latest/changesets.html)
            or OT format (https://github.com/ottypes/text) can be str for
            etherpad or array for collab-react-components
        :param belong_to_operation: To which operation it belongs to
        :type belong_to_operation: Operation
        """
        if operation_type == "add":
            self.operation_type = "add"
            self.text_to_add = text_to_add
        elif operation_type == "del":
            self.operation_type = "del"
            self.length_to_delete = length_to_delete
        else:
            raise AttributeError("Undefined elementary operation")
        # The position of the op when it was added
        self.abs_position = abs_position
        self.line_number = line_number
        self.position_inline = position_inline
        self.author = author
        self.timestamp = timestamp
        self.pad_name = pad_name
        self.revs = revs
        self.changeset = changeset
        self.belong_to_operation = belong_to_operation
        self.editor = editor
        # The position of the op in the current pad.
        self.current_position = self.abs_position
        self.deleted = False
        self.assigned_para = [[],[]]
        self.paragraph_id = ""

    def __str__(self):
        return ("Operation: {}".format(self.operation_type) +
                "\nPosition: {}".format(self.abs_position) +
                ("\nText to add: {}".format(self.text_to_add) if
                    self.operation_type == 'add' else
                    "\nLength to delete: {}".format(self.length_to_delete)) +
                "\nLine number: {}".format(self.line_number) +
                "\nPosition inline: {}".format(self.position_inline) +
                "\nAuthor: {}".format(self.author) +
                "\nTimestamp: {}".format(self.timestamp) +
                "\nPad Name: {}".format(self.pad_name) +
                "\nRevs: {}".format(self.revs) +
                "\nOriginal changeset: {}".format(self.changeset) +
                "\nEditor: {}".format(self.editor) +
                "\nBelong to Operation: {}".format(self.belong_to_operation))

    def assign_para(self, para_to_assign):
        para_to_assign = [sorted(set(list_para)) for
                          list_para in para_to_assign]
        for list_para in para_to_assign:
            if type(list_para[0]) == int and list_para[0] < 0:
                list_para[0]
        self.assigned_para = para_to_assign

    def assign_paragraph_id(self, paragraph_id):
        self.paragraph_id = paragraph_id

    def get_length_of_op(self):
        """
        Gives the number of character added (can be negative for deletes)

        :rtype: int
        """
        if self.operation_type == "add":
            return len(self.text_to_add)
        elif self.operation_type == "del":
            return -self.length_to_delete
        else:
            raise AttributeError("Undefined elementary operation")

    @classmethod
    def sort_elem_ops(cls, elem_ops_list):
        """
        Sort a list of elementary operations

        :param elem_ops_list: The list of elem_ops to sort
        :type elem_ops_list: list[ElementaryOperation]
        :return: The sorted list of elementary operation
        :rtype: list[ElementaryOperation]
        """
        elem_ops = [[elem_op.timestamp, elem_op] for elem_op in elem_ops_list]
        # sort them
        sorted_elem_ops = sorted(elem_ops, key=lambda e: e[0])
        return [elem_op_tuple[1] for elem_op_tuple in sorted_elem_ops]

    def copy(self):
        """
        Copy the elementary operation if it's an add. Used in operation
        builder. It doesn't copy a few parameters which are unrelevant at this
        stage
        :return: The copy of the ElementaryOperation
        :rtype: ElementaryOperation
        """
        new_op = ElementaryOperation(operation_type=self.operation_type,
                                     abs_position=self.abs_position,
                                     text_to_add=self.text_to_add,
                                     line_number=self.line_number,
                                     position_inline=self.position_inline,
                                     author=self.author,
                                     timestamp=self.timestamp,
                                     pad_name=self.pad_name,
                                     revs=self.revs,
                                     changeset=self.changeset,
                                     belong_to_operation=self.belong_to_operation,
                                     editor=self.editor)
        return new_op


class Operation:
    """
    An Operation. It groups multiple ElementaryOperation of a same user that
    we consider as a single operation.
    """

    def __init__(self, elem_op):
        """
        Create an Operation.

        :param elem_op: first ElementaryOperation
        :type elem_op: ElementaryOperation
        """
        # Whether the operation has already been added to its pad (useful for
        # operation_builder)
        self.pushed = False
        # Author of the op
        self.author = elem_op.author
        # Position of the start of the operation
        self.position_start_of_op = elem_op.abs_position
        # Position of the first elementary operation.
        self.position_first_op = elem_op.abs_position
        # Time of the start of the operation
        self.timestamp_start = elem_op.timestamp
        # Time of the end of the operation
        self.timestamp_end = elem_op.timestamp
        # list of all the elementary operation that makes this operation
        self.elem_ops = []
        # :type: list[ElementaryOperation]

        # tell to the elem_op to which op it now belongs
        elem_op.belong_to_operation = self
        self.elem_ops.append(elem_op)
        # Type of the operation (Write, Edit, Deletion, Copy/Paste, Jump Line)
        self.type = None

        # Dictionary containing various information about the context of the
        # operation
        self.context = dict()
        #:type: dict('synchronous')

    def add_elem_op(self, elem_op):
        """
        Add an ElementaryOperation to the list of elem_ops.

        :param elem_op: new ElementaryOperation to add to the op
        :type elem_op: ElementaryOperation
        """
        # update the end_timestamp
        self.timestamp_end = elem_op.timestamp
        # Tell to the elem_op to which op it now belongs
        elem_op.belong_to_operation = self
        self.elem_ops.append(elem_op)

        # If we delete something left of us, we move the position of the op to
        # the left
        if elem_op.abs_position < self.position_start_of_op:
            self.position_start_of_op = elem_op.abs_position

    def add_elem_ops(self, elem_ops):
        """
        Add a list of ElementaryOperation to the list of elem_ops.

        :param elem_ops:
        """
        for elem_op in elem_ops:
            self.add_elem_op(elem_op)

    def get_length_of_op(self):
        """
        Return the number of characters added (can be negative in case of
        deletions)

        :return: the N of chars
        :rtype: int
        """
        length = 0
        for elem_op in self.elem_ops:
            length += elem_op.get_length_of_op()
        return length

    def get_assigned_para(self, get_para_before=True, get_min_para=True):

        paras_before = []
        paras_after = []

        for elem_op in self.elem_ops:
            paras_before.extend(elem_op.assigned_para[0])
            paras_after.extend(elem_op.assigned_para[1])

        paras_before = sorted(set(paras_before))
        paras_after = sorted(set(paras_after))

        paras_list = paras_before if get_para_before else paras_after

        if len(paras_list) > 0:
            if get_min_para:
                return paras_list[0]
            else:
                return paras_list[-1]
        else:
            return None

    def get_paragraph_history(self):
        paras_hists = []
        for elem_op in self.elem_ops:
            paras_hists.append(elem_op.paragraph_id)

        if len(paras_hists) > 0:
            return paras_hists[0]
        else:
            return None

    def get_paragraph_original(self):
        def remove_split_suffix(p_id):
            new_p_id = p_id
            while True:
                if "." in p_id:
                    split_p_id = p_id.split(".")
                    if (split_p_id[-1].isalpha() and
                        split_p_id[-1].isupper()):
                        new_p_id = ".".join(split_p_id[:-1])
                if new_p_id == p_id:
                    break
                p_id = new_p_id
            return p_id

        paras_orig = []
        for elem_op in self.elem_ops:
            p_id = elem_op.paragraph_id
            p_id = remove_split_suffix(p_id)
            if ("+" in p_id and
                p_id[0] == "(" and p_id[-1] == ")"):
                p_o = p_id[1:].split("+")[0]
                p_id = remove_split_suffix(p_o)
                p_id = [entry for entry in p_id.split('(') if entry != ''][0]
            paras_orig.append(p_id)

        if len(paras_orig) > 0:
            return paras_orig[0]
        else:
            return None

    def get_text_added(self):
        """
        Get text added from the elem_ops.

        :return: The text
        :rtype:string
        """
        text = ""
        for elem_op in self.elem_ops:
            if elem_op.operation_type == "add":
                text += elem_op.text_to_add
        return text

    def get_deletion_length(self):
        """
        Get deletion length from elem_ops.

        :return: Length
        :rtype:int
        """
        length = 0
        for elem_op in self.elem_ops:
            if elem_op.operation_type == "del":
                length += elem_op.length_to_delete
        return length

    def __str__(self):
        return ("Author: {}".format(self.author) +
                "\nPosition: From {} to {}".format(
                    self.position_start_of_op,
                    self.position_start_of_op + self.get_length_of_op()) +
                "\nWritten: from {} to {}".format(
                    self.timestamp_start,
                    self.timestamp_end) +
                "\nWith {} elementary operations".format(len(self.elem_ops)) +
                "\nType: {}".format(self.type) +
                "\nText to add: {}".format(self.get_text_added()) +
                "\nLength of deletion: {}".format(self.get_deletion_length()) +
                "\nParagraphs: {}".format(self.get_assigned_para()) +
                "\nContext: {}".format(self.context))

    def get_line(self, separator_char='\t', string_delimiter=''):
        def format_delimiter(field):
            # we need string_delimiter if separator_char is included in a field
            if type(field) == str and separator_char in field:
                return string_delimiter + field + string_delimiter
            else:
                return format(field)

        return separator_char.join(map(lambda x: format_delimiter(x), [
                    self.author,
                    self.position_start_of_op,
                    (self.position_start_of_op + self.get_length_of_op()),
                    self.timestamp_start,
                    self.timestamp_end,
                    len(self.elem_ops),
                    self.type,
                    # In get_text_added(), remove '\n' from the text because
                    # there may be problems reading the csv file
                    self.get_text_added().replace("\n", "") if self.type != "jump" else None,
                    # If no problems, comment previous line and uncomment the following:
                    # self.get_text_added() if self.type != "jump" else None,
                    self.get_deletion_length(),
                    self.get_assigned_para(),
                    self.get_paragraph_history(),
                    self.get_paragraph_original(),
                    self.context["proportion_pad"],
                    self.context["proportion_paragraph"]]))

    def update_indices(self, elem_op):
        """
        Move the position of the Operation if an edit happens before it

        :param elem_op: the element we check
        :type elem_op: ElementaryOperation
        """
        # Check that we are indeed after the edit. If so we must move
        # our position accordingly
        if (elem_op.operation_type == "add" and
            elem_op.abs_position < self.position_start_of_op):
            self.position_start_of_op += len(elem_op.text_to_add)
            self.position_first_op += len(elem_op.text_to_add)
        elif (elem_op.operation_type == "del" and
            elem_op.abs_position + elem_op.length_to_delete < self.position_start_of_op):
            self.position_start_of_op -= elem_op.length_to_delete
            self.position_first_op -= elem_op.length_to_delete

    @classmethod
    def sort_ops(cls, ops_list):
        """
        Sort a list of operations according to their starting time

        :param ops_list: The list of ops to sort
        :type ops_list: list[Operation]
        :return: The sorted list of operations
        :rtype: list[Operation]
        """
        ops = [[op.timestamp_start, op] for op in ops_list]
        # sort them
        sorted_ops = sorted(ops, key=lambda e: e[0])
        return [op_tuple[1] for op_tuple in sorted_ops]



class Paragraph:
    def __init__(self, elem_op=None, new_line=False, paragraph=None, paragraph_id=""):
        """
        Create a new paragraph from an ElementaryOperation or a Paragraph

        :param elem_op: First elementary operation that we add
        :type elem_op: ElementaryOperation
        :param paragraph: paragraph we copy from
        :type paragraph: Paragraph
        :param new_line: Is this paragraph only a newline ?
        :type new_line: bool
        """
        assert elem_op is not None or paragraph is not None, ("Error"
            "creating new Paragraph. Either elem_op or paragraph must be"
            "non-null")

        self.paragraph_id = paragraph_id
        self.is_deleted = False

        if elem_op is not None:
            self.elem_ops = [elem_op]
            """list[ElementaryOperation]"""
            self.operations = [elem_op.belong_to_operation]
            """list[Operation]"""
            self.abs_position = elem_op.abs_position
            """int"""
            self.length = len(elem_op.text_to_add)
            """int"""
            self.new_line = new_line
            """bool"""
        else:
            self.elem_ops = paragraph.elem_ops
            """list[ElementaryOperation]"""
            self.operations = paragraph.operations
            """list[Operation]"""
            self.abs_position = paragraph.abs_position
            """int"""
            self.length = paragraph.length
            """int"""
            self.new_line = paragraph.new_line
            """bool"""

    def add_elem_op(self, elem_op):
        """
        add an elementary operation (and its parent operation) to the paragraph

        :param elem_op: elementary operation to add
        :type elem_op: ElementaryOperation
        """

        def find_position_in_list(elem_ops, elem_op_):
            """
            Find the position we should insert the elem_op in

            :param elem_ops: Current list of operation
            :type elem_ops: list[ElementaryOperation]
            :param elem_op_: ElementaryOperation we want to add
            :type elem_op_: ElementaryOperation
            :return: the index where we should insert
            :rtype: int
            """
            for i, op in enumerate(elem_ops):
                if (not op.deleted and
                    op.current_position >= elem_op_.current_position):
                    return i
            return len(elem_ops)


        elem_op_idx_in_list = find_position_in_list(self.elem_ops, elem_op)
        self.elem_ops.insert(elem_op_idx_in_list, elem_op)

        # Mark the element as deleted
        # (used in finding where to insert in the paragraph)
        if elem_op.operation_type == "del":
            for op in self.elem_ops:
                if (elem_op.abs_position <= op.current_position <=
                    elem_op.abs_position + elem_op.length_to_delete):
                    op.deleted = True

        # Update the current position of the following elementary position
        for i in range(elem_op_idx_in_list + 1, len(self.elem_ops)):
            if (elem_op.operation_type == "add" or
                (elem_op.operation_type == 'del' and
                    elem_op.abs_position + elem_op.length_to_delete <=
                    self.elem_ops[i].current_position)):
                # We will update the indices after
                # (if they are not the elem_ops being deleted)
                self.elem_ops[i].current_position += elem_op.get_length_of_op()

        if not (elem_op.belong_to_operation in self.operations):
            self.operations.append(elem_op.belong_to_operation)

        if elem_op.operation_type == "del":
            # If it's a deletion, it will change the start position and length
            if elem_op.abs_position < self.abs_position:
                # it deletes the beginning of my paragraph
                self.abs_position = elem_op.abs_position + elem_op.length_to_delete
                self.length -= (elem_op.abs_position +
                                elem_op.length_to_delete -
                                self.abs_position)
            elif (elem_op.abs_position + elem_op.length_to_delete >
                  self.abs_position + self.length):
                # it deletes the end of my paragraph
                self.length -= (self.abs_position +
                                self.length -
                                elem_op.abs_position)
            else:
                # deletion is fully contained in my paragraph
                self.length -= elem_op.length_to_delete

        elif elem_op.operation_type == "add":
            self.length += (len(elem_op.text_to_add))

        else:
            raise NotImplementedError

    def get_length(self):
        """
        Get the length of the paragraph

        :return: the length of the paragraph
        :rtype: int
        """
        return self.length

    def get_abs_length(self):
        """
        Get the sum of absolute value of the lengths of the elementary
        operation contained in the paragraph

        :return:
        """
        abs_length = 0
        for op in self.operations:
            abs_length += abs(op.get_length_of_op())
        return abs_length

    def __str__(self, verbose=0):
        string = ("from: {}".format(self.abs_position) +
                  "\nto: {}".format(self.abs_position + self.length))
        if verbose > 0:
            string += "\nOperations:\n"
            string += "\n".join([op.__str__() for op in self.operations])
        else:
            string += "\nNumber of Operations: {}".format(len(self.operations))

        return string

    def update_indices(self, elem_op):
        """
        Move the position of the paragraph if a edit happens before it

        :param elem_op: the element we check
        :type elem_op: ElementaryOperation
        """
        # Check that we are indeed after the edit. If so we must move our
        # position accordingly
        if (elem_op.operation_type == "add" and
            elem_op.abs_position <= self.abs_position):
            self.abs_position += len(elem_op.text_to_add)
            for op in self.elem_ops:
                op.current_position += len(elem_op.text_to_add)
        elif (elem_op.operation_type == "del" and
              elem_op.abs_position + elem_op.length_to_delete <= self.abs_position):
            self.abs_position -= elem_op.length_to_delete
            for op in self.elem_ops:
                op.current_position -= elem_op.length_to_delete
        # else:
        #     # Shouldn't happen, maybe remove the condition elif or check
        #     # that we ask the right paragraphs to update
        #     raise AssertionError

    def copy(self):
        return Paragraph(paragraph=self, paragraph_id=self.paragraph_id)

    @classmethod
    def merge(cls, first_paragraph, last_paragraph, elem_op):
        """
        Merge two paragraphs

        :param first_paragraph:
        :type first_paragraph: Paragraph
        :param last_paragraph:
        :type last_paragraph: Paragraph
        :return: the merged paragraph
        :rtype: Paragraph
        """

        new_para = first_paragraph.copy()
        new_para.abs_position = first_paragraph.abs_position
        new_para.length = (first_paragraph.length + last_paragraph.length -
                           (elem_op.abs_position +
                            elem_op.length_to_delete -
                            last_paragraph.abs_position))

        new_para.elem_ops = first_paragraph.elem_ops
        # Mark as deleted every elementary operation that is considered as
        # deleted.
        for op in last_paragraph.elem_ops:
            # Mark the element as deleted (used in finding where to insert
            # in the paragraph)
            if (elem_op.abs_position <= op.current_position <=
                elem_op.abs_position + elem_op.length_to_delete):
                op.deleted = True
            else:
                # update the current position of the elem_op
                op.current_position -= elem_op.length_to_delete
            new_para.elem_ops.append(op)

        new_para.operations = first_paragraph.operations
        for op in last_paragraph.operations:
            if not op in new_para.operations:
                new_para.operations.append(op)

        # TODO: remove assertions
        assert (first_paragraph.new_line is False and
                last_paragraph.new_line is False)
        return new_para

    @classmethod
    def split(cls, paragraph_to_split, position,
        return_new_line_paragraph_id=False):
        """
        split the paragraph in two on the position passed as parameter

        :param paragraph_to_split: paragraph to split
        :type paragraph_to_split: Paragraph
        :param position: position at which we split the paragraph in two
        :return: the 2 new paragraphs
        :rtype: (Paragraph,Paragraph)
        """
        new_paragraph_ids = Paragraph.compute_para_id("split",
                                            paragraph_to_split.paragraph_id)

        para1 = paragraph_to_split.copy()
        para1.paragraph_id = new_paragraph_ids[0]
        para2 = paragraph_to_split.copy()
        para2.paragraph_id = new_paragraph_ids[2]

        para1.elem_ops = []
        para2.elem_ops = []
        para2.abs_position = position + 1  # Since we add a new line
        para1.operations = []
        para2.operations = []
        para1.length = position - paragraph_to_split.abs_position
        para2.length = (paragraph_to_split.abs_position +
                        paragraph_to_split.length -
                        position)

        # for each elementary operation add it to the corresponding paragraph
        for elem_op in paragraph_to_split.elem_ops:
            length = elem_op.get_length_of_op()

            # TODO review because position moves. Maybe keep track of the
            # effective position ?
            # if elem_op.current_position + length <= position:
            #     para1.elem_ops.append(elem_op)
            #     if not (elem_op.belong_to_operation in para1.operations):
            #         para1.operations.append(elem_op.belong_to_operation)
            if position <= elem_op.current_position:
                elem_op.current_position += 1  # Because we add the new line
                para2.elem_ops.append(elem_op)
                if not (elem_op.belong_to_operation in para2.operations):
                    para2.operations.append(elem_op.belong_to_operation)
            else:
                para1.elem_ops.append(elem_op)
                if not (elem_op.belong_to_operation in para1.operations):
                    para1.operations.append(elem_op.belong_to_operation)
                    # TODO remove
                    # para2.elem_ops.append(elem_op)
                    # if not (elem_op.belong_to_operation in para2.operations):
                    #     para2.operations.append(elem_op.belong_to_operation)

        if return_new_line_paragraph_id:
            return para1, para2, new_paragraph_ids[1]
        else:
            return para1, para2

    @classmethod
    def compute_para_id(cls, relation, reference_id1=None, reference_id2=None):
        def compute_new_end_chars(end_chars):
            """Used when splitting
            For example, it makes it possible to use suffixes 0.D, 0.E, 0.F
            instead of 0.C.A, 0.C.B, 0.C.C
            """
            assert len(end_chars)
            char_increments = [1,2,3]

            def int2base(x, base, c_digs=None):
                if c_digs is None:
                    digs = [chr(i) for i in range(ord('A'), ord('Z')+1)]
                else:
                    digs = c_digs

                digits = []
                while x:
                    digits.append(digs[int(x % base)])
                    x = int(x / base)
                digits.reverse()
                return ''.join(digits)

            # Represent as number
            base = ord('Z') - ord('A') + 1
            offset_char_int = ord('A')
            int_representation = sum([
                base ** idx * (ord(c) - offset_char_int)
                for idx, c in enumerate(end_chars[::-1])])

            new_int_representations = [int_representation + ci
                                       for ci in char_increments]
            return [int2base(nir, base)
                    for nir in new_int_representations]


        split_suffixes_init = ["A", "B", "C"]
        split_suffix = "."
        after_suffix = "_"

        # After many operations the ID may become incredibly long.
        # One quick fix is to generate a random number and use it instead.
        # of the ID that we would use otherwise
        random_id = ''.join(random.choice(string.digits)
                       for _ in range(int(config.max_len_id / 2)))

        if relation == "insert_before":
            assert reference_id1 is not None
            if len(reference_id1) > config.max_len_id:
                return random_id

            for first_number_idx, c in enumerate(reference_id1):
                if c.isdigit():
                    break
            last_number_idx = first_number_idx
            while reference_id1[last_number_idx].isdigit():
                last_number_idx += 1
                if last_number_idx == len(reference_id1):
                    break

            if (first_number_idx > 0 and
                reference_id1[first_number_idx - 1] == "-"):
                # The number is negative, so we include the sign
                first_number_idx -= 1

            paragraph_id_number_int = int(
                reference_id1[first_number_idx:last_number_idx])

            return str(paragraph_id_number_int - 1)

        elif relation == "insert_after":
            assert reference_id1 is not None
            if len(reference_id1) > config.max_len_id:
                return random_id

            # We check if the reference_id ends in "_" followed by an int
            after_suffix_idx = reference_id1.rfind(after_suffix)
            paragraph_id_number = reference_id1[after_suffix_idx + 1:]
            try:
                paragraph_id_number_int = int(paragraph_id_number)
            except:
                # It does not end in "_" followed by an int
                # which is equivalent to not having "_" in the id at all
                after_suffix_idx = -1
            if after_suffix_idx == -1:
                return reference_id1 + after_suffix + "0"
            else:
                return (reference_id1[:after_suffix_idx + 1] +
                        str(paragraph_id_number_int + 1))

        elif relation == "insert_between":
            assert reference_id1 is not None and reference_id2 is not None
            if (len(reference_id1) > config.max_len_id or
                len(reference_id2) > config.max_len_id):
                return random_id
            # Same as for "insert_after":
            after_suffix_idx = reference_id1.rfind(after_suffix)
            after_paragraph_id_number = reference_id1[after_suffix_idx + 1:]
            try:
                after_paragraph_id_number_int = int(after_paragraph_id_number)
            except:
                # It does not end in "_" followed by an int
                # which is equivalent to not having "_" in the id at all
                after_suffix_idx = -1
            # Now for before:
            before_suffix_idx = reference_id2.rfind(after_suffix)
            before_paragraph_id_number = reference_id2[before_suffix_idx + 1:]
            try:
                before_paragraph_id_number_int = int(before_paragraph_id_number)
            except:
                # It does not end in "_" followed by an int
                # which is equivalent to not having "_" in the id at all
                before_suffix_idx = -1

            if (before_suffix_idx != -1 and after_suffix_idx != -1 and
                reference_id1[:after_suffix_idx] == reference_id2[:before_suffix_idx]):
                # e.g. insert between 0 and 1 => 0_1
                return reference_id1 + after_suffix + "0"
            elif (before_suffix_idx != -1 and after_suffix_idx != -1 and
                reference_id2[:before_suffix_idx] == reference_id1[:before_suffix_idx]):
                # e.g. insert between 0_1_1 and 0_2 => 0_1_2
                return (reference_id1[:after_suffix_idx + 1] +
                        str(after_paragraph_id_number_int + 1))
            elif (before_suffix_idx != -1 and after_suffix_idx != -1 and
                reference_id2[:after_suffix_idx] == reference_id1[:after_suffix_idx]):
                # e.g. insert between 0_1 and 0_1_1 => 0_1_0
                return (reference_id2[:before_suffix_idx + 1] +
                        str(before_paragraph_id_number_int - 1))
            elif len(reference_id1) <= len(reference_id2):
                return reference_id1 + after_suffix + "0"
            else:
                return reference_id2 + after_suffix + "-1"

        elif relation == "initial":
            return "0"

        elif relation == "merge":
            assert reference_id1 is not None and reference_id2 is not None
            if (len(reference_id1) > config.max_len_id or
                len(reference_id2) > config.max_len_id):
                return ""
            return "({}+{})".format(reference_id1, reference_id2)

        elif relation == "split":
            assert reference_id1 is not None
            if len(reference_id1) > config.max_len_id:
                return [random_id + split_suffix + suf
                        for suf in split_suffixes_init]

            # See if reference_id1 finishes in "." followed by letters
            # We check if the reference_id ends in "_" followed by an int
            split_suffix_idx = reference_id1.rfind(split_suffix)
            end_chars = reference_id1[split_suffix_idx + 1:]
            if (split_suffix_idx != -1 and
                end_chars.isalpha() and
                end_chars.isupper()):
                # Instead of using A, B and C we use the corresponding ones
                new_end_chars = compute_new_end_chars(end_chars)
                return [reference_id1[:split_suffix_idx + 1] + suf
                        for suf in new_end_chars]

            else:
                return [reference_id1 + split_suffix + suf
                        for suf in split_suffixes_init]

    def __lt__(self, other):
        return self.abs_position < other.abs_position

