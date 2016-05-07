import cPickle as pickle
import numpy as np
import json

champs = json.load(open('champ_data.json','r'))

print(champs['data'])

champ_data = champs['data']

sorting = sorted(champs['data'])

num_champs = len(sorting)

ordered_champs = []
cid_to_index = {}

# ID, name, key
for i,champ in enumerate(sorting):
    ordered_champs.append([champ_data[champ]['id'],champ_data[champ]['name'], champ ])
    cid_to_index[champ_data[champ]['id']] = i

print(ordered_champs)

pickle.dump(ordered_champs, open('ordered_champs.p', 'w'))
pickle.dump(cid_to_index, open('cid_mapping.p', 'w'))
