# get the best match from the database for a particular summoner
import numpy as np
import cPickle as pickle
import sys
import json
import urllib2

# trying different methods of doing the match
match_modes = ['basic', 'weighted', 'weighted2', 'weighted3', 'presquared']
match_mode = match_modes[3]

NUM_CHAMPIONS = 130

sum_name = sys.argv[1]
clean_sum_name = sum_name.replace(" ", "").lower()

api_key = open('key.txt','r').read().rstrip()
data = pickle.load(open('na_profiles.p','r'))
names = pickle.load(open('na_summoners.p', 'r'))
champs = pickle.load(open('ordered_champs.p', 'r'))
cid_to_index = pickle.load(open('cid_mapping.p','r'))

print(api_key)

sum_id = 36049629
region='na'
region2='na1'
#query_info = ('na','na1',sum_id,api_key)

#TODO: put error checking
sum_id_query = "https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}".format(region, clean_sum_name, api_key)
print(sum_id_query)
f = urllib2.urlopen(sum_id_query)
j = json.loads(f.read())
sum_id = int(j[clean_sum_name]['id'])

query = "https://{0}.api.pvp.net/championmastery/location/{1}/player/{2}/champions?api_key={3}".format(region, region2, sum_id, api_key)

f = urllib2.urlopen(query)
j = json.loads(f.read())

user_data = np.zeros((1,NUM_CHAMPIONS))

total_points = 0
for champ in j:
    cid = champ['championId']
    pts = champ['championPoints']

    #convert champion id to champion index
    cindex = cid_to_index[cid]

    user_data[0,cindex] = pts
    total_points += pts

user_data[0,:] /= np.sum(user_data[0,:])

# Do matching
if match_mode == 'basic':
    result = np.linalg.norm(data - user_data, axis=1)
elif match_mode == 'weighted':
    result = np.linalg.norm(np.multiply(data - user_data, user_data), axis=1)
elif match_mode == 'weighted2':
    result = np.linalg.norm(np.multiply(data - user_data, np.multiply(user_data, user_data)), axis=1)
elif match_mode == 'weighted3':
    result = np.linalg.norm(np.multiply(data - user_data, np.multiply(np.multiply(user_data, user_data), user_data)), axis=1)
elif match_mode == 'presquared':
    result = np.linalg.norm(data - user_data, axis=1)

indices = np.argsort(result)
index = np.argmin(result)

print(indices[:5])

print(data[index,:5])
print(user_data[0,:5])
#print(names[index][1])

for i in indices[:5]:
    print(names[i][1])
