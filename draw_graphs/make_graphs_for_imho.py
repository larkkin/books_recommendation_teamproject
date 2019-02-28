import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams["figure.figsize"] = (15, 15)
rcParams["font.size"] = 22
filename = "result/result_new_imho_dcg.txt"

users = []
user_dic = {}
lines = []

sorting = {}

with open(filename, "r") as inf:
    lines = inf.readlines()

ideal = {}
forbidden = set()

for line in lines:
    algo, user, dcg = line.split()
    if algo == "ideal":
        ideal[int(user)] = float(dcg)
        if round(float(dcg)) == float(dcg):
            forbidden.add(int(user))
    users.append(int(user))
users = sorted(set(users).difference(forbidden), key = lambda u: ideal[u])
for i in range(len(users)):
    user_dic[users[i]] = i
results = {}

for line in lines:
    algo, user, dcg = line.split()
    if int(user) in forbidden:
        continue
    if algo == "ideal":
        continue
    if algo not in results:
        results[algo] = []
    results[algo].append((user_dic[int(user)], float(dcg)))

print(len(ideal.items()), len(users))

for algo, al_list in results.items():
    if algo == "ideal":
        print("Mistake!")
        continue
    new_list = []
    for user, dcg in al_list:
        new_list.append((user, dcg / ideal[users[user]]))
    results[algo] = new_list

for algo, al_list in results.items():
    mean = sum([y for x, y in al_list])/len(al_list)
    s = sum([(y - mean)**2 for x, y in al_list])/(len(al_list) - 1)
    print(algo, mean, s, s**0.5)

plt.cla()

#res_p, res_r = [list(t) for t in zip(*results["KNNBasic"])]
#plt.plot(res_p, res_r, linestyle='None', marker='o', color="red") [0]
#res_p, res_r = [list(t) for t in zip(*results["SVDpp"])]
#plt.plot(res_p, res_r, linestyle='None', marker='o', color="orange") [0]
#res_p, res_r = [list(t) for t in zip(*results["KNNWithMeans"])]
#plt.plot(res_p, res_r, linestyle='None', marker='o', color="green") [0]
#res_p, res_r = [list(t) for t in zip(*results["KNNWithZScore"])]
#plt.plot(res_p, res_r, linestyle='None', marker='o', color="pink") [0]
#res_p, res_r = [list(t) for t in zip(*results["KNNBaseline"])]
#plt.plot(res_p, res_r, linestyle='None', marker='o', color="cyan") [0]
res_p, res_r = [list(t) for t in zip(*results["NMF"])]
plt.plot(res_p, res_r, linestyle='None', marker='o', color="orange")[0]#"brown") [0]
res_p, res_r = [list(t) for t in zip(*results["CoClustering"])]
plt.plot(res_p, res_r, linestyle='None', marker='o', color="black")[0]#"olive") [0]
res_p, res_r = [list(t) for t in zip(*results["SVD"])]
plt.plot(res_p, res_r, linestyle='None', marker='o', color="cyan")[0]#"blue") [0]
res_p, res_r = [list(t) for t in zip(*results["SlopeOne"])]
plt.plot(res_p, res_r, linestyle='None', marker='o', color="red")[0]#"gray") [0]
plt.xlim(100000, len(users) + 10)
plt.ylim(0.4, 1.01)
plt.xlabel("users")
plt.ylabel("ndcg value")
plt.savefig("graphs/surprise_new_imho.png")
