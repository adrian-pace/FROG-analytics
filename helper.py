# # import MySQLdb
# # import ast
# #
# # from scipy import spatial
# #
# # from analytics.parser import *
# # import gensim.models as g
# # import numpy as np
# #
# # model = 'pre_modle/doc2vec/doc2vec.bin'
# # m = g.Doc2Vec.load(model)
# # test_docs = 'I like having class in school, because it is quilt interesting.'
# # test_1 = 'Apple is planted in the earth, and will have flower in the autumn.'
# # test_2 = 'I have courses this afternoon in university.'
# # start_alpha=0.01
# # infer_epoch=1000
# #
# # #infer test vectors
# # anchor = m.infer_vector(test_docs, alpha=start_alpha, steps=infer_epoch)
# # t1 =m.infer_vector(test_1, alpha=start_alpha, steps=infer_epoch)
# # t2 =m.infer_vector(test_2, alpha=start_alpha, steps=infer_epoch)
# # dist1 = spatial.distance.cosine(t1, anchor)
# # dist2 =  spatial.distance.cosine(t2, anchor)
# # print('it is done')
#
# message = 'Diury uf Vise Ongal'
# N =3
# key =[['6','o','u'],['0','a','u'],['6','l','s']]
#
# for K in key:
#     pos = int(K[0])
#     mess1 = message[:pos]
#     mess2 = message[pos:]
#     mess = ""
#     s1 = [ord(K[1])]
#     s2 = [ord(K[2])]
#     if s1[0]>90:
#         s1.append(s1[0]-32)
#     else:
#         s1.append(s1[0]+32)
#     if s2[0]>90:
#         s2.append(s2[0]-32)
#     else:
#         s2.append(s2[0]+32)
#     for s in mess2:
#         if ord(s)>90:
#             if ord(s) in s1:
#                 mess +=chr(max(s2))
#             elif ord(s) in s2:
#                 mess +=chr(max(s1))
#             else:
#                 mess +=s
#         else:
#             if ord(s) in s1:
#                 mess +=chr(min(s2))
#             elif ord(s) in s2:
#                 mess +=chr(min(s1))
#             else:
#                 mess +=s
#     message = mess1+mess
# print(message)

# K=1000
# DP = [0 for i in range(K+1)]
# DP[:4] = [0,0,1,1]
# for j in range(1,K+1):
#     if j < 4:
#         continue
#     else:
#         if j % 3!=0 and j%2!=0:
#             DP[j] = 1 + DP[j - 1]
#         elif j%3 ==0 and j%2!=0:
#             t = int(j / 3)
#             DP[j] = 1 +min(DP[j-1],DP[t])
#         elif j %2==0 and j %3!=0:
#             t = int(j/2)
#             DP[j] = 1 + min(DP[j-1],DP[t])
#         else:
#             t1 = int(j/2)
#             t2 = int(j/3)
#             DP[j] = 1 + min(DP[j-1], DP[t2],DP[t1])
# print(DP[K])
def permuteUnique(nums):
    List = []
    nums.sort()
    used = [False for i in range(len(nums))]
    backtrack(List,[],nums,used)
    return List

def backtrack(List,tmp,nums,used):
    if(len(tmp)==len(nums)):
        List.append(tmp.copy())
    else:
        for i in range(len(nums)):
            if(used[i] or (i>0 and nums[i]==nums[i-1]) and (not used[i-1])):
                continue
            used[i] = True
            tmp.append(nums[i])
            backtrack(List,tmp,nums,used)
            used[i] = False
            tmp.pop()

print(permuteUnique([1,1,2]))