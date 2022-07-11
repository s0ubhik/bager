import json
fp = open("train_name_data.json")
rows = json.load(fp)
dic = {}
for row in rows:
	name, code, dist = row
	dic.update({code: [name, dist]})

d = json.dumps(dic)
print(d)
