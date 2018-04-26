import pandas as pd
import random
from surprise import NormalPredictor
from surprise import KNNBasic
from surprise import SVD
from surprise import NMF
from surprise import CoClustering
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate

f = open('data_users_and_books.txt', 'r')
linesf = f.readlines()

ratings_dict = {'user':[], 'item':[], 'rating':[]}

for l in linesf:
    a, b, c = l.split()
    if a == "None":
        continue
    ratings_dict['user'].append(a)
    ratings_dict['item'].append(b)
    ratings_dict['rating'].append(int(c))

df = pd.DataFrame(ratings_dict)
reader = Reader(rating_scale=(0, 100))
data = Dataset.load_from_df(df[['user', 'item', 'rating']], reader)
cross_validate(NormalPredictor(), data, cv=2, verbose=True)
cross_validate(KNNBasic(), data, cv=2, verbose=True)
cross_validate(SVD(), data, cv=2, verbose=True)
cross_validate(SVD(), data, cv=2, verbose=True)
cross_validate(NMF(), data, cv=2, verbose=True)
cross_validate(CoClustering(), data, cv=2, verbose=True)
