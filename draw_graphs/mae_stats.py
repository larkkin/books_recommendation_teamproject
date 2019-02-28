filename = "result/result_bookmate_sum2_rae.txt"
lines = []
with open(filename, "r") as f:
    lines = f.readlines()

cur_algo = ""
res = {}
for line in lines:
    splitted = line.split()
    if splitted[0] == "start":
        cur_algo = splitted[2]
        continue
    if splitted[0] == "result":
        res[cur_algo] = splitted[1]

for algo, result in res.items():
    print(algo, result)
