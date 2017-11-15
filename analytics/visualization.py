import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def display_user_participation(pad):
    """
    Display a pie chart representing the participation according to the length of each authors

    :param pad:
    :return: None
    """
    # Fetch all the authors who participated in the pad
    authors = pad.get_authors()

    # Initialize the number of letters written by each authors
    author_lengths = np.zeros(len(authors))

    # increment the participation accordingly
    for op in pad.operations:
        author_lengths[authors.index(op.author)] += op.get_length_of_op()

    # Compute the overall participation
    overall_length = sum(author_lengths)
    proportions = author_lengths / overall_length

    # Transform the array in dataframe
    df = pd.DataFrame({'Participation proportion': proportions,
                       'Authors': authors
                       })
    df.index = df['Authors']

    # Plot the results as a pie chart
    df.plot.pie(y='Participation proportion', autopct='%1.0f%%')
    plt.title('Proportion of participation by authors')
    plt.show()


def display_overall_op_type(pad):
    """
    Plot the type counts of all operations of the pad.

    :param pad:
    :return: None
    """
    # Initialize the bins and fill them
    types = ['write', 'edit', 'delete', 'paste', 'jump']
    type_counts = np.zeros(len(types))
    for op in pad.operations:
        type_counts[types.index(op.type)] += 1

    # Transform the array in dataframe
    df = pd.DataFrame({'Type Counts': type_counts,
                       'Types': types
                       })
    df.index = df['Types']

    # Plot the results as a seaborn barplot
    ax = sns.barplot(x='Types', y='Type Counts', data=df)
    plt.title('Type repartition of operations of the pad')
    plt.show()


def display_types_per_user(pad):
    """
    Plot the type counts of all operations of the pad for all users separately.

    :param pad:
    :return: None
    """
    # Initialize the bins and fill them
    types = ['write', 'edit', 'delete', 'paste', 'jump']

    # Create dataframe and fill it
    df = pd.DataFrame(columns=('Operations', 'Types', 'Authors'))
    for i, op in enumerate(pad.operations):
        df.loc[i] = [op, op.type, op.author]

    # Plot the results as a seaborn countplot
    ax = sns.countplot(x='Types', hue="Authors", data=df)
    plt.title('Type repartition of operations of the pad per user')
    plt.show()


def display_proportion_sync_in_pad(pad):
    """
    Display in a pie chart the proportion of synchronous writing in the entire pad

    :param pad:
    :return: None
    """
    prop_sync = 0
    prop_async = 0
    for op in pad.operations:
        if op.context['synchronous_in_pad']:
            prop_sync += op.context['proportion_pad']
        else:
            prop_async += op.context['proportion_pad']
    df = pd.DataFrame({'sync/async proportion': [prop_sync, prop_async]}, index=['synchronous', 'asynchronous'])

    # Plot the results as a pie chart
    df.plot.pie(y='sync/async proportion', autopct='%1.0f%%', color=['yellow', 'grey'])
    plt.title('Proportion of {a}synchronous writing in the pad')
    plt.show()


def display_proportion_sync_in_paragraphs(pad):
    """
    Display in a barplot the proportion of synchronous writing in all the paragraphs (not the jump lines)

    :param pad:
    :return: None
    """
    # Init variables
    prop_sync_paragraphs = []
    paragraph_names = []
    i = 1
    for paragraph in pad.paragraphs:
        if not paragraph.new_line:
            # Create the label of the paragraph
            paragraph_names.append('p' + str(i))
            i += 1
            prop_sync = 0
            for op in paragraph.operations:
                if op.context['synchronous_in_paragraph']:
                    prop_sync += op.context['proportion_paragraph']
            prop_sync_paragraphs.append(prop_sync)
    prop_async_paragraphs = [1 - x for x in prop_sync_paragraphs]

    # Transform the data to a dataframe
    df = pd.DataFrame({'sync proportion': prop_sync_paragraphs, 'async proportion': prop_async_paragraphs},
                      index=paragraph_names)

    # Plot the results as a pie chart
    df.plot.barh(y=['sync proportion', 'async proportion'], stacked=True, color=['yellow', 'grey'])
    plt.gca().invert_yaxis()
    plt.title('Proportion of {a}synchronous writing in paragraphs')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
    plt.show()


def display_user_participation_paragraphs(pad):
    """
    Display in a barplot the proportion of author writing in all the paragraphs (not the jump lines)

    :param pad:
    :return: None
    """
    #Init variables
    author_names = pad.get_authors()
    prop_authors_paragraphs = []
    paragraph_names = []
    i = 1
    for paragraph in pad.paragraphs:
        # Initialize a dictionary containing participation proportion for each authors
        prop_authors = {author_name : 0 for author_name in author_names}
        # Only take into account the real paragraphs (not the new lines)
        if not paragraph.new_line:
            # Create the label of the paragraph
            paragraph_names.append('p' + str(i))
            i += 1
            for op in paragraph.operations:
                prop_authors[op.author] += op.context['proportion_paragraph'] # increment with the corresponding prop
            prop_authors_paragraphs.append(prop_authors)

    # Transform the final data into a pandas dataframe
    df = pd.DataFrame(prop_authors_paragraphs,
                      index=paragraph_names)

    # Plot the results as a stacked plot bar
    df.plot.barh(y=author_names, stacked=True)
    plt.gca().invert_yaxis()
    plt.title('Proportion of absolute writings (overall additions) per authors in paragraphs')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(author_names))
    plt.show()


def display_user_participation_paragraphs_with_del(pad):
    """
    Display in a barplot the proportion of author writing in all the paragraphs (not the jump lines) with the del
    operations

    :param pad:
    :return: None
    """
    # Init variables
    author_names = pad.get_authors()
    prop_authors_paragraphs_add = []
    prop_authors_paragraphs_del = []
    paragraph_names = []
    i = 1
    for paragraph in pad.paragraphs:
        # Initialize a dictionary containing participation proportion for each authors
        prop_authors_add = {author_name: 0 for author_name in author_names}
        prop_authors_del = {author_name: 0 for author_name in author_names}
        # Only take into account the real paragraphs (not the new lines)
        if not paragraph.new_line:
            # Create the label of the paragraph
            paragraph_names.append('p' + str(i))
            i += 1
            for elem_op in paragraph.elem_ops:
                if elem_op.operation_type == 'add':
                    prop_authors_add[elem_op.author] += len(elem_op.text_to_add) # increment with the corresponding len
                if elem_op.operation_type == 'del':
                    prop_authors_del[elem_op.author] += elem_op.length_to_delete  # increment with the corresponding len
            total_count = sum(prop_authors_add.values()) + sum(prop_authors_del.values())
            if total_count != 0:
                prop_authors_add = {k: v / total_count for k, v in prop_authors_add.items()}
                prop_authors_del = {k: v / total_count for k, v in prop_authors_del.items()}
            prop_authors_paragraphs_add.append(prop_authors_add)
            prop_authors_paragraphs_del.append(prop_authors_del)



    # Transform the final data into a pandas dataframe
    df_add = pd.DataFrame(prop_authors_paragraphs_add, index=paragraph_names)
    df_add.columns += ' write/add'
    df_del = pd.DataFrame(prop_authors_paragraphs_del, index=paragraph_names)
    df_del.columns += ' del'
    df = pd.concat([df_add, df_del], axis=1)
    df = df.sort_index(axis=1)

    # Plot the results as a stacked plot bar
    df.plot.barh(y=df.columns, stacked=True, color=sns.color_palette("Paired", 40))
    plt.gca().invert_yaxis()
    plt.title('Proportion of writings per authors in paragraphs with deletions and additions seperated')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(author_names))
    plt.show()