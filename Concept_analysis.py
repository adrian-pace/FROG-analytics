from analytics.operation_builder import sort_elem_ops_per_pad
import run_analytics
import config
from analytics import operation_builder
from analytics.parser import *
from analytics.visualization import *
import os
from concept import *
from helpers import *
from lsa import *
from ontology import *
#from responses_processing import *
#from tags_processing import *
#from topic_modelling import *
from visualization import *
from preprocessing import *
from french_preprocessing import *
#from dashboard import *
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gensim
import time
import requests
import csv
import json
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from collections import OrderedDict

list_of_elem_ops_per_pad = dict()
elemOpsCounter = 0
root_of_dbs = "data/"

for (dirpath, dirnames, filenames) in os.walk(root_of_dbs):
    for filename in filenames:
        if '.sql' in filename:
            path_to_db = os.path.join(dirpath, filename)
            # Fetching the new operations
            list_of_elem_ops_per_main = get_elem_ops_per_pad_from_db(
                path_to_db=path_to_db,
                 editor='sql_dump'
                # editor = 'etherpad'
            )# we got the ElementOperations of each pad at beginining

            for pad_name, pad_vals in list_of_elem_ops_per_main.items():
                list_of_elem_ops_per_pad[pad_name + filename[-7:-4]] = pad_vals
        break

pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad,##  pads with all the operations
                                                                             config.maximum_time_between_elem_ops)

for pad_name in pads:
    paraTextPerPad = {}
    elemOpsCounter += len(elem_ops_treated[pad_name])
    pad = pads[pad_name]
    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
    paras = pad.paragraphs
    text = pad.get_text()
    ## real-time print the text of each paragraph
    for para in paras:
        # timeStampList = [elem_op.timestamp for elem_op in para.elem_ops]
        # timeStampList.sort()
        # for time in timeStampList:
        #     text1 = para.get_para_text(time)
        para.create_para_text()
    print(1)







# list_of_elem_ops_per_main  = get_elem_ops_per_pad_from_db(editor='MySQL')


print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))
paragraph = pads[pad_name].paragraphs
authors = pads[pad_name].authors

df = pd.DataFrame({'Paragraph': paragraph,
                       'Authors': paragraph
                       })
print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))


