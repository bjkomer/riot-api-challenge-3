# get all mastery data for master and challenger players
#TODO: possibly combine regions for more results

import numpy as np
import cPickle as pickle
import sys
import json
import urllib2
import time

# Open an IPython session if an exception is found
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)

NUM_CHAMPIONS = 130
#NUM_SUMMONERS = 1000

region = 'na'
region2 = 'na1'
api_key = open('key.txt','r').read().rstrip()

def get_region_code(region):
    region = region.upper()
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


region = sys.argv[1]

region1, region2 = get_region_code(region)

names = pickle.load(open(region+'_summoners.p', 'r'))
#names = pickle.load(open(region+'_diamond_summoners.p', 'r'))
cid_to_index = pickle.load(open('cid_mapping.p','r'))

def get_mastery_data(sid):
    query = "https://{0}.api.pvp.net/championmastery/location/{1}/player/{2}/champions?api_key={3}".format(region1, region2, sid, api_key)
    f = urllib2.urlopen(query)
    j = json.loads(f.read())
    profile = np.zeros(NUM_CHAMPIONS)
    for champ in j:
        cid = champ['championId']
        pts = champ['championPoints']
        profile[cid_to_index[cid]] = pts
    # normalize
    profile /= np.sum(profile)
    return profile

data = np.zeros((len(names), NUM_CHAMPIONS))
print(len(names))
for i, name in enumerate(names):
    success = False
    while not success:
        try:
            profile = get_mastery_data(name[0])
            data[i,:] = profile
            print(i)
            success = True
            time.sleep(1.6)
        except:
            print("an error occurred, retrying")
            time.sleep(1.6)
            success = False
            #pickle.dump(data, open(region+'_'+str(i)+'_diamond_profiles.p','w'))
            #pickle.dump(data, open(region+'_'+str(i)+'_profiles.p','w'))
            #sys.exit()


pickle.dump(data, open(region+'_profiles.p','w'))
#pickle.dump(data, open(region+'_diamond_profiles.p','w'))
