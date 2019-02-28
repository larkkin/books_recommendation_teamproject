import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams["figure.figsize"] = (10, 10)
rcParams["font.size"] = 22
file1 = "bookmate_sum/data.txt"
file2 = "bookmate_data/data_users_and_books_min_full.txt"

with open(file1, "r") as inf:
    lines1 = inf.readlines()

with open(file2, "r") as inf:
    lines2 = inf.readlines()

set1 = set()
set2 = set()

for line in lines1:
    user, item, rate = line.split()
    set1.add((user, item))

for line in lines2:
    user, item, rate = line.split()
    set2.add((user, item))
check = set1.intersection(set2)
print(len(check))
su = set()
si = set()
for u, i in check:
    su.add(u)
    si.add(i)
print(len(su), len(si))

percent1 = [0] * 101
percent2 = [0] * 101

for line in lines1:
    user, item, rate = line.split()
    if (user, item) in check:
        percent1[int(rate)] += 1

for line in lines2:
    user, item, rate = line.split()
    if (user, item) in check:
        percent2[int(rate)] += 1



plt.cla()
all = [i for i in range(101)]
plt.bar(all, percent1)
plt.xlabel("% read")
plt.ylabel("number of pairs")
plt.savefig("graphs/data_bookmate_sum.png")
plt.cla()
all = [i for i in range(101)]
plt.bar(all, percent2)
plt.xlabel("% read")
plt.ylabel("number of pairs")
plt.savefig("graphs/data_bookmate.png")

