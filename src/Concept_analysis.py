from analytics.operation_builder import sort_elem_ops_per_pad
import run_analytics
import config
from analytics import operation_builder
from analytics.parser import *
from analytics.visualization import *
import os
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import sent2vec


def numberOperation(x):
    num = 0
    for win in x:
        num +=len(win.operations)
    return num


list_of_elem_ops_per_pad = dict()
elemOpsCounter = 0
root_of_dbs = "../data/"

model = sent2vec.Sent2vecModel()
model_name = '../pre_modle/sent2vec/wiki_unigrams.bin'
model.load_model(model_name)

for (dirpath, dirnames, filenames) in os.walk(root_of_dbs):
    for filename in filenames:
        if '.sql' in filename:
            path_to_db = os.path.join(dirpath, filename)
            # Fetching the new operations
            list_of_elem_ops_per_main = get_elem_ops_per_pad_from_db(
                path_to_db=path_to_db,
                 editor='sql_dump'
            )# we got the ElementOperations of each pad at beginining

            for pad_name, pad_vals in list_of_elem_ops_per_main.items():
                list_of_elem_ops_per_pad[pad_name + filename[-7:-4]] = pad_vals
        break
pads, _, elem_ops_treated = operation_builder.build_operations_from_elem_ops(list_of_elem_ops_per_pad,##  pads with all the operations
                                                                             config.maximum_time_between_elem_ops)


outputDistance = {}
outputSimilarity = {}
outputText = {}
outputWindowOps = {}
outputNumWin = {}
winLength = {}
operationNum = {}
average = {}
i = 0
for pad_name in pads:
    i +=1
    paraTextPerPad = {}
    elemOpsCounter += len(elem_ops_treated[pad_name])
    pad = pads[pad_name]
    # text = pad.text_by_ops()

    # create the paragraphs
    pad.create_paragraphs_from_ops(elem_ops_treated[pad_name]) # we need to set starttime by this function
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
    pad.BuildWindowOperation(200000)
    pad.getTextByWin(model)   # this is used to compute the length and build text for each win

    # ---- below is used to compute the added text length
    pad.PlotTextAdded()


    pad.computeDistance()
    # pad.PlotLengthOperationTime()
    pad.PlotSimilarityDistribution()

    # winList = []
    # for wins in pad.windowOperation.values():
    #     winList.append(numberOperation(wins))
    # outputWindowOps[pad_name] =winList
    # operationNum[pad_name] = sum(winList)
    # if len(winList)==0:
    #     average[pad_name] = 0
    # else:
    #     average[pad_name] = sum(winList)/len(winList)

    # outputDistance[pad_name]=pad.
    # outputSimilarity[pad_name] = pad.similarity
    # outputText[pad_name] = pad.WindowOperationText

    print("------%d",i)
    if(i==200):
        break

    # winLength[pad_name] = len(winList)

outputWin = pd.DataFrame.from_dict(outputWindowOps,orient='index').fillna("No")
outputWin = outputWin.reset_index()
outputWin['winNum']= outputWin['index'].map(winLength)
outputWin['opsNum'] = outputWin['index'].map(operationNum)
outputWin['averageOps'] = outputWin['index'].map(average)
outputWin.to_csv('winNum-120.csv', encoding='utf-8')
# outputTextDF = pd.DataFrame.from_dict(outputWindowOps,orient='index').fillna("No win!")
# outputTextDF  = outputTextDF.T
# outputTextDF.to_csv('Text-s.csv', encoding='utf-8')
# outputDistanceDF= pd.DataFrame(outputDistance).fillna(0)
# outputDistanceDF = outputDistanceDF.T
# outputDistanceDF.to_csv('Distance-s.csv',float_format='%.2f',encoding='utf-8')
# outputSimilarityDF= pd.DataFrame(outputSimilarity).fillna(0)
# outputSimilarityDF = outputSimilarityDF.T
# outputSimilarityDF.to_csv('similarity-s.csv',float_format='%.2f',encoding='utf-8')


# list_of_elem_ops_per_main  = get_elem_ops_per_pad_from_db(editor='MySQL')


print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))
paragraph = pads[pad_name].paragraphs
authors = pads[pad_name].authors

df = pd.DataFrame({'Paragraph': paragraph,
                       'Authors': paragraph
                       })
print("There are %s pads with a total of %s elementary operations" % (str(len(pads)), str(elemOpsCounter)))

