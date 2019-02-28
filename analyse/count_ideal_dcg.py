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


fout = open("result_new_imho_ideal_dcg.txt", "w")
def sort_by_users(testset):
    result = {}
    for uid, iid, true_r in testset:
        if (uid not in result):
            result[uid] = []
        result[uid].append((int(iid), float(true_r)))
    for uid, user_ratings in result.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        result[uid] = user_ratings
    return result

predictions = sort_by_users(testset)
for uid, rates in predictions.items():
    dcg = 0
    for i in range(len(rates)):
        iid, true_r = rates[i]
        dcg += true_r * log(2) / log(i + 2)
    print("ideal", uid, dcg, file=fout, flush=True)
