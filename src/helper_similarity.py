'''
 This file store some functions that used in ipython text file about semantic analysis
'''
from scipy import spatial
from analytics.visualization import *
import matplotlib.pyplot as plt
import seaborn as sns
from analytics.Pad import cleanText
import sent2vec
import numpy as np
import spacy

start_alpha=0.01
infer_epoch=1000

model_name = '../pre_modle/doc2vec/enwiki/doc2vec.bin'
model1 = g.Doc2Vec.load(model_name)
model_name = '../pre_modle/doc2vec/apnews_dbow/doc2vec.bin'
model2 = g.Doc2Vec.load(model_name)
model3 = spacy.load('en_core_web_md')
model4 = sent2vec.Sent2vecModel()
model_name4 = '../pre_modle/sent2vec/wiki_unigrams.bin'
model4.load_model(model_name4)
model5 = sent2vec.Sent2vecModel()
model_name5 = '../pre_modle/sent2vec/torontobooks_unigrams.bin'
model5.load_model(model_name5)

def Similarity(text1,text2,model_name):
    '''
    Compute similarity between two texts
    :param text1:
    :param text2:
    :param model_name:  the name of pre-trained model
    :return: similarity value
    '''
    
    text1 = cleanText(text1)
    text2 = cleanText(text2)
    if model_name == 'doc2vec-wiki':
        model = model1
        vec1 = model.infer_vector(text1, alpha=start_alpha, steps=infer_epoch)
        vec2 = model.infer_vector(text2, alpha=start_alpha, steps=infer_epoch)
    elif model_name == 'doc2vec-news':
        model = model2
        vec1 = model.infer_vector(text1, alpha=start_alpha, steps=infer_epoch)
        vec2 = model.infer_vector(text2, alpha=start_alpha, steps=infer_epoch)
    elif model_name=='spacy':
        model = model3
        text1 = ' '.join(text1)
        text2 = ' '.join(text2)
        vec1 = model(text1).vector
        vec2 = model(text2).vector
    elif model_name == 'sent2vec-wiki':
        model = model4
        text1 = ' '.join(text1)
        text2 = ' '.join(text2)
        vec1 = model.embed_sentence(text1) 
        vec2 = model.embed_sentence(text2)
        #print(vec1,vec2)
    elif model_name == 'sent2vec-book':
        model = model5
        text1 = ' '.join(text1)
        text2 = ' '.join(text2)
        vec1 = model.embed_sentence(text1) 
        vec2 = model.embed_sentence(text2) 
    
    similarity = 1-spatial.distance.cosine(vec1,vec2)
#     dis = np.linalg.norm(vec1,vec2)
    return similarity


def computeSimilarity(data):
    '''
    compute similarity by different pre-trained models and store as a column of dataframe
    :param data: type: dataframe
    :return:  dataframe
    '''
    data['apnews-doc2vec'] = data.apply(lambda row:Similarity(row['text1'],row['text2'],'doc2vec-news'),axis=1)

    data['enwiki-doc2vec'] = data.apply(lambda row:Similarity(row['text1'],row['text2'],'doc2vec-wiki'),axis=1)

    data['spacy_model'] = data.apply(lambda row:Similarity(row['text1'],row['text2'],'spacy'),axis=1)

    data['sent2vec-wiki'] = data.apply(lambda row:Similarity(row['text1'],row['text2'],'sent2vec-wiki'),axis=1)

    data['sent2vec-book'] = data.apply(lambda row:Similarity(row['text1'],row['text2'],'sent2vec-book'),axis=1)
    return data


def computeSimilarityMatrix(pad,size):
    '''
    This is used to compute similarity between superparagraph in one pad
    :param pad:
    :param size:  the number of whole pad's superparagraph
    :return: similarity matrix
    '''
    superparagraph_list = pad.get_paragraphs_text()
    length = len(superparagraph_list)
    similar_matrix =np.zeros([size,size])
    for i in range(size):
        for j in range(i,size):
            if i <length and j<length:
                text1 = superparagraph_list[i]
                text2 = superparagraph_list[j]
                similar = Similarity(text1,text2,'sent2vec-wiki')
                similar_matrix[i][j] = similar
                similar_matrix[j][i] = similar
            else:
                similar_matrix[i][j] = 0
                similar_matrix[j][i] = 0
    return similar_matrix

def plotSimilarityHeatmap(matrix):
    fig, ax = plt.subplots(figsize=(10,7))
    sns.heatmap(matrix,ax=ax,linewidth=0.5)

    ax.set_xlabel('SuperParagraph ID')
    ax.set_ylabel('SuperParagraph ID')
    plt.show()
