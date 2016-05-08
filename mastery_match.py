import os
from os import curdir, sep
import json
import numpy as np
import cPickle as pickle
import os.path
import urllib2

from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash, jsonify

my_dir = os.path.dirname(__file__)
os.path.join(my_dir, 'key.txt')

api_key = open(os.path.join(my_dir, 'key.txt'),'r').read().rstrip()
data = pickle.load(open(os.path.join(my_dir, 'na_combined_profiles.p'),'r'))
names = pickle.load(open(os.path.join(my_dir, 'na_combined_summoners.p'), 'r'))
champs = pickle.load(open(os.path.join(my_dir, 'ordered_champs.p'), 'r'))
cid_to_index = pickle.load(open(os.path.join(my_dir, 'cid_mapping.p'),'r'))

app = Flask(__name__, static_folder=os.path.join(my_dir, 'static'))
app.config.from_object(__name__)

# trying different methods of doing the match
match_modes = ['basic', 'weighted', 'weighted2', 'weighted3', 'presquared']
match_mode = match_modes[3]#match_modes[3]

NUM_CHAMPIONS = 130
IMAGE_PREFIX = 'http://ddragon.leagueoflegends.com/cdn/5.22.3/img/champion/' #TODO: update path


region='na'
region2='na1'

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


@app.route('/')
def startup():
    return render_template('index.html')

@app.route('/suggestions', methods=['POST'])
def suggestions():
    #summoner_name = request.get_data()
    data = request.get_data()

    summoner_name, region = data.split('&')

    summoner_name = summoner_name[14:]
    region = region[7:]
    region1, region2 = get_region_code(region)

    #TODO: add option to return results from regions other than your own
    response = retrieve_data(summoner_name, region=region1, region2=region2)

    return jsonify(response)


def retrieve_data(sum_name, region='na', region2='na1'):

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

        matches = []
        #names : id, name, league, region
        for i in indices[:5]:
            matches.append([names[i]])

        return {'summoner_name':sum_name,
                'matches': matches,
                'error':False}
    except:
        return {'error':True}

if __name__ == '__main__':
    app.run()