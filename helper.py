import MySQLdb
import ast

from scipy import spatial

from analytics.parser import *
import gensim.models as g
import numpy as np

model = 'pre_modle/doc2vec/doc2vec.bin'
m = g.Doc2Vec.load(model)
test_docs = 'I like having class in school, because it is quilt interesting.'
test_1 = 'Apple is planted in the earth, and will have flower in the autumn.'
test_2 = 'I have courses this afternoon in university.'
start_alpha=0.01
infer_epoch=1000

#infer test vectors
anchor = m.infer_vector(test_docs, alpha=start_alpha, steps=infer_epoch)
t1 =m.infer_vector(test_1, alpha=start_alpha, steps=infer_epoch)
t2 =m.infer_vector(test_2, alpha=start_alpha, steps=infer_epoch)
dist1 = spatial.distance.cosine(t1, anchor)
dist2 =  spatial.distance.cosine(t2, anchor)
print('it is done')