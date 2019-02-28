import pandas as pd
import random
from math import *

from operator import attrgetter

from surprise import NormalPredictor
from surprise import KNNBasic
from surprise import KNNBaseline
from surprise import SVD
from surprise import SVDpp
from surprise import NMF
from surprise import KNNWithMeans
from surprise import KNNWithZScore
from surprise import SlopeOne
from surprise import CoClustering
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split
from surprise import accuracy
from surprise.model_selection import PredefinedKFold

files_dir = "../new_data_imho/"
train_file = files_dir + 'train.txt'
test_file = files_dir + 'test.txt'

f = open(train_file, 'r')
linesf = f.readlines()
f.close()

ratings_dict = {'user':[], 'item':[], 'rating':[]}

for l in linesf:
    a, b, r = l.split()
    ratings_dict['user'].append(a)
    ratings_dict['item'].append(b)
    ratings_dict['rating'].append(int(r))

df = pd.DataFrame(ratings_dict)
reader = Reader(rating_scale=(1, 10))
trainset = Dataset.load_from_df(df[['user', 'item', 'rating']], reader).build_full_trainset()

data = Dataset.load_from_folds([(train_file, test_file)], reader=Reader())
_, testset = [item for item in PredefinedKFold().split(data)][0]

print(len([k for k in trainset.all_ratings()]), len([k for k in testset]))


fout = open("result_new_imho_dcg.txt", "w")
lout = open("logs_new_imho_dcg.txt", "w")
algos = [
#KNNBasic(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}), 
SVD(n_factors=80, n_epochs=25, lr_all=0.02, reg_all=0.2), 
#SVDpp(n_factors=80, n_epochs=20, lr_all=0.03, reg_all=0.1),
#KNNWithMeans(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}),
#KNNWithZScore(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}),
#KNNBaseline(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}, bsl_options={'method': 'sgd'}), 
NMF(n_factors=90, n_epochs=20, reg_pu=0.07, reg_qi=0.05, reg_bu=0.02, reg_bi=0.02, lr_bu=0.006, lr_bi=0.004), 
SlopeOne(), CoClustering(n_cltr_u=3, n_cltr_i=12, n_epochs=15)]

def sort_by_users(predictions):
    result = {}
    for uid, iid, true_r, est, _ in predictions:
        if (uid not in result):
            result[uid] = []
        result[uid].append((int(iid), float(true_r), float(est)))
    for uid, user_ratings in result.items():
        user_ratings.sort(key=lambda x: x[2] * 100 + 10 - x[1], reverse=True)
        result[uid] = user_ratings
    return result

for algo in algos:
    print("start algo", algo.__class__.__name__)
    print("start algo", algo.__class__.__name__, file=lout, flush=True)
    algo.fit(trainset)
    predictions = sort_by_users(algo.test(testset))
    for uid, rates in predictions.items():
        dcg = 0
        for i in range(len(rates)):
            iid, true_r, est = rates[i]
            dcg += true_r * log(2) / log(i + 2)
            print(uid, iid, true_r, est, dcg, file=lout, flush=True)
        print(algo.__class__.__name__, uid, dcg, file=fout, flush=True)
        print(uid, dcg)
    #print("result", accuracy.mae(predictions), file=fout)
    #accuracy.rmse(predictions)
fout.close()
lout.close()
