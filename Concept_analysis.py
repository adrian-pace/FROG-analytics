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
import gensim.models as g
import pandas as pd
import sent2vec

list_of_elem_ops_per_pad = dict()
elemOpsCounter = 0
root_of_dbs = "data/"

## this is the first method to load the pre-trained model
# model = 'pre_modle/doc2vec/apnews_dbow/doc2vec.bin'
# m = g.Doc2Vec.load(model)
# start_alpha=0.01
# infer_epoch=1000
# m = spacy.load('en_core_web_md')
model = sent2vec.Sent2vecModel()
model_name = 'pre_modle/sent2vec/wiki_unigrams.bin'
model.load_model(model_name)

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


outputDistance = {}
outputSimilarity = {}
outputText = {}
i = 0
for pad_name in pads:
    i +=1
    if i==200:
        break
    paraTextPerPad = {}
    elemOpsCounter += len(elem_ops_treated[pad_name])
    pad = pads[pad_name]
    # text = pad.text_by_ops()

    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name])
    # pad.build_operation_context(config.delay_sync, config.time_to_reset_day, config.time_to_reset_break)

    # paras = pad.paragraphs
    # text = pad.get_text()
    ## real-time print the text of each paragraph

    # for para in paras:
    #     para.create_para_text()
    # author_context = []

    #------below is used to computer different author context#
    # pad.PreprocessOperationByAuthor(compute_vector=True,model=m,start_alpha=start_alpha,infer_epoch=infer_epoch)
    # outputDistance[pad_name] = pad.AuthorDistance
    # outputSimilarity[pad_name] = pad.AuthorSimilarity
    # outputText[pad_name] = pad.AuthorText

    # ----bellow is compute the window-based author context
    pad.BuildWindowOperation(60000)
    pad.getTextByWin(model)
    pad.computeDistance()
    # pad.PlotLengthOperationTime()
    pad.PlotSimilarityDistribution()
    outputDistance[pad_name]=pad.distance
    outputSimilarity[pad_name] = pad.similarity
    outputText[pad_name] = pad.WindowOperationText

    print("------%d",i)


outputTextDF = pd.DataFrame(outputText).fillna("No text!")
outputTextDF  = outputTextDF.T
outputTextDF.to_csv('Text-s.csv', encoding='utf-8')
outputDistanceDF= pd.DataFrame(outputDistance).fillna(0)
outputDistanceDF = outputDistanceDF.T
outputDistanceDF.to_csv('Distance-s.csv',float_format='%.2f',encoding='utf-8')
outputSimilarityDF= pd.DataFrame(outputSimilarity).fillna(0)
outputSimilarityDF = outputSimilarityDF.T
outputSimilarityDF.to_csv('similarity-s.csv',float_format='%.2f',encoding='utf-8')


# list_of_elem_ops_per_main  = get_elem_ops_per_pad_from_db(editor='MySQL')


print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))
paragraph = pads[pad_name].paragraphs
authors = pads[pad_name].authors

df = pd.DataFrame({'Paragraph': paragraph,
                       'Authors': paragraph
                       })
print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))


