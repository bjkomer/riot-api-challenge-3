import os
from os import curdir, sep
import json
import numpy as np
import cPickle as pickle
import os.path
import urllib2
from copy import deepcopy

from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash, jsonify

my_dir = os.path.dirname(__file__)
os.path.join(my_dir, 'key.txt')

"""
get_region_code = {'BR':('br','BR1'),
                   'EUNE':('eune','EUN1'),
                   'EUW':('euw','EUW1'),
                   'JP':('jp','JP1'),
                   'KR':('kr','KR'),
                   'LAN':('lan','LA1'),
                   'LAS':('las','LA2'),
                   'NA':('na','NA1'),
                   'OCE':('oce','OC1'),
                   'RU':('ru','RU'),
                   'TR':('tr','TR1'),
                  }
"""
# Use function instead of dict to handle the 'else' case
# if something somehow goes wrong, default to NA
def get_region_code(region):
    if region == 'BR':
        return 'br', 'BR1'
    elif region == 'EUNE':
        return 'eune', 'EUN1'
    elif region == 'EUW':
        return 'euw', 'EUW1'
    elif region == 'JP':
        return 'jp', 'JP1'
    elif region == 'KR':
        return 'kr', 'KR'
    elif region == 'LAN':
        return 'lan', 'LA1'
    elif region == 'LAS':
        return 'las', 'LA2'
    elif region == 'NA':
        return 'na', 'NA1'
    elif region == 'OCE':
        return 'oce', 'OC1'
    elif region == 'RU':
        return 'ru', 'RU'
    elif region == 'TR':
        return 'tr', 'TR1'
    else:
        return 'na', 'NA1'

regions = ['br','eune','euw','jp','kr','lan','las','na','oce','ru','tr']
diamond_regions = ['br','eune','euw','lan','las','na','oce','ru','tr']

api_key = open(os.path.join(my_dir, 'key.txt'),'r').read().rstrip()
#data = pickle.load(open(os.path.join(my_dir, 'na_combined_profiles.p'),'r'))
#names = pickle.load(open(os.path.join(my_dir, 'na_combined_summoners.p'), 'r'))
champs = pickle.load(open(os.path.join(my_dir, 'ordered_champs.p'), 'r'))
cid_to_index = pickle.load(open(os.path.join(my_dir, 'cid_mapping.p'),'r'))

# very space inefficient and gross loading all the data like this
# but should be more time efficient and easy to use when running
data = {}
data_diamond = {}
data_diamond_only = {}
names = {}
names_diamond = {}
names_all = []
names_diamond_all = []
# load regional data
for region in regions:
    #if region == 'naaaaaa':
    #    data[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_combined_profiles.p'),'r'))
    #    names[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_combined_summoners.p'),'r'))
    #else:
    data[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_profiles.p'),'r'))
    names[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_summoners.p'),'r'))
    data_diamond[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_profiles.p'),'r'))
    names_diamond[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_summoners.p'),'r'))
    for n in names[region]:
        names_all.append(n)
        names_diamond_all.append(n)

for region in diamond_regions:
    data_diamond_only[region] = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_diamond_profiles.p'),'r'))
    data_diamond[region] = np.concatenate([data[region],data_diamond_only[region]])
    names_diamond_region = pickle.load(open(os.path.join(my_dir, 'data/'+region+'_diamond_summoners.p'),'r'))
    for n in names_diamond_region:
        names_diamond[region].append(n)
        names_diamond_all.append(n)

data_all = np.concatenate([data[r] for r in regions])
data_diamond_all = np.concatenate([data_all, np.concatenate([data_diamond_only[r] for r in diamond_regions])])



#names_all = np.concatenate([names[r] for r in regions])

app = Flask(__name__, static_folder=os.path.join(my_dir, 'static'))
#app.config.from_object(__name__)
#app.config['PROPAGATE_EXCEPTIONS'] = True

# trying different methods of doing the match
match_modes = ['basic', 'weighted', 'weighted2', 'weighted3', 'top10', 'top1', 'complex', 'top5match','multiply']
match_mode =  'complex'

NUM_CHAMPIONS = 130

@app.route('/')
def startup():
    return render_template('index.html')

@app.route('/suggestions', methods=['POST'])
def suggestions():
    #summoner_name = request.get_data()
    data = request.get_data()

    summoner_name, region, use_all, diamond = data.split('&')

    summoner_name = summoner_name[14:]
    region = region[7:]
    use_all = use_all[8:] == 'true'
    diamond = diamond[8:] == 'true'

    region1, region2 = get_region_code(region)

    #TODO: add option to return results from regions other than your own
    response = retrieve_data(summoner_name, region=region1, region2=region2, use_all=use_all, diamond=diamond)

    return jsonify(response)


def retrieve_data(sum_name, region='na', region2='na1', use_all=False, diamond=False):

    clean_sum_name = sum_name.replace(" ", "").lower()

    try:
        # Get Summoner ID
        sum_id_query = "https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}".format(region, clean_sum_name, api_key)
        
        f = urllib2.urlopen(sum_id_query)
        j = json.loads(f.read())

        sum_id = int(j[clean_sum_name]['id'])

        # Get Mastery Data
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

        if use_all:
            # Compare against summoners from all regions
            if diamond:
                sum_data = data_diamond_all
                name_data = names_diamond_all
            else:
                sum_data = data_all#np.concatenate([data[r] for r in regions])
                name_data = names_all#np.concatenate([names[r] for r in regions])
        else:
            if diamond:
                sum_data = data_diamond[region]
                name_data = names_diamond[region]
            else:
                sum_data = data[region]
                name_data = names[region]

        # Do matching
        if match_mode == 'basic':
            result = np.linalg.norm(data[region] - user_data, axis=1)
        elif match_mode == 'weighted':
            result = np.linalg.norm(np.multiply(data[region] - user_data, user_data), axis=1)
        elif match_mode == 'weighted2':
            result = np.linalg.norm(np.multiply(data[region] - user_data, np.multiply(user_data, user_data)), axis=1)
        elif match_mode == 'weighted3':
            result = np.linalg.norm(np.multiply(data[region] - user_data, np.multiply(np.multiply(user_data, user_data), user_data)), axis=1)
        elif match_mode == 'top10':
            tmp_data = deepcopy(data[region])
            tmp_user = deepcopy(user_data)
            indices = np.argsort(tmp_user)
            tmp_user[indices[:-5]] = 0
            tmp_user /= np.sum(tmp_user)
            for i in range(len(tmp_data)):
                indices = np.argsort(tmp_data[i])
                tmp_data[i][indices[:-5]] = 0
                tmp_data[i] /= np.sum(tmp_data[i])
            result = np.linalg.norm(tmp_data - tmp_user, axis=1)
        elif match_mode == 'top1':
            max_user = np.argmax(user_data)
            tmp_data = deepcopy(data[region])
            res_data = np.zeros(len(tmp_data))

            for i in range(len(tmp_data)):
                max_data = np.argmax(tmp_data[i])
                if max_data == max_user:
                    res_data[i] = 0
                else:
                    res_data[i] = 1
            result = res_data
        elif match_mode == 'top5match':
            tmp_data = deepcopy(data[region])
            tmp_user = deepcopy(user_data)
            indices = np.argsort(tmp_user)
            tmp_user[:] = 1
            tmp_user[indices[:-5]] = 0
            #tmp_user[indices[-5:]] = 1
            for i in range(len(tmp_data)):
                indices = np.argsort(tmp_data[i])
                tmp_data[i][:] = 1
                tmp_data[i][indices[:-5]] = 0
                #tmp_data[i][indices[-5:]] = 1
            result = 0 - np.linalg.norm(np.multiply(tmp_data, tmp_user), axis=1)
        elif match_mode == 'multiply':
            result = 0 - np.linalg.norm(np.multiply(data[region], user_data), axis=1)
            print(result.shape)

        elif match_mode == 'complex':
            tmp_data = deepcopy(sum_data)
            tmp_user = deepcopy(user_data)
            indices = np.argsort(tmp_user)
            tmp_user[indices[:-5]] = 0
            tmp_user /= np.sum(tmp_user)
            for i in range(len(tmp_data)):
                indices = np.argsort(tmp_data[i])
                tmp_data[i][indices[:-5]] = 0
                tmp_data[i] /= np.sum(tmp_data[i])
            result = np.linalg.norm(tmp_data - tmp_user, axis=1)*.2 + np.linalg.norm(sum_data - user_data, axis=1)*.3 - np.linalg.norm(np.multiply(sum_data, user_data), axis=1)

        indices = np.argsort(result)

        matches = []
        #names : id, name, league, region
        for i in indices[:5]:
            matches.append([name_data[i]])

        return {'summoner_name':sum_name,
                'matches': matches,
                'error':False}
    except:
        return {'error':True}

if __name__ == '__main__':
    app.run()