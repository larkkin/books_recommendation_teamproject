import pandas as pd
import random

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

files_dir = "../bookmate_data/"
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


fout = open("result_bookmate_rae.txt", "w")

algos = [KNNBasic(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}), 
SVD(n_factors=80, n_epochs=25, lr_all=0.02, reg_all=0.2), 
SVDpp(n_factors=80, n_epochs=20, lr_all=0.03, reg_all=0.1),
KNNWithMeans(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}),
KNNWithZScore(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}),
KNNBaseline(k=15, min_k=1, sim_options={'name': 'cosine', 'user_based': True}, bsl_options={'method': 'sgd'}), 
NMF(n_factors=90, n_epochs=20, reg_pu=0.07, reg_qi=0.05, reg_bu=0.02, reg_bi=0.02, lr_bu=0.006, lr_bi=0.004), 
SlopeOne(), CoClustering(n_cltr_u=3, n_cltr_i=12, n_epochs=15)]

for algo in algos:
    print("start algo", algo.__class__.__name__)
    print("start algo", algo.__class__.__name__, file=fout, flush=True)
    algo.fit(trainset)
    predictions = algo.test(testset)
    for p in predictions:
        print(p, file=fout, flush=True)
    print("result", accuracy.mae(predictions), file=fout)
    accuracy.rmse(predictions)
fout.close()

