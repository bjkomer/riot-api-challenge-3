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

#names = pickle.load(open(region+'_summoners.p', 'r'))
names = pickle.load(open(region+'_diamond_summoners.p', 'r'))
cid_to_index = pickle.load(open('cid_mapping.p','r'))

def get_mastery_data(sid):
    query = "https://{0}.api.pvp.net/championmastery/location/{1}/player/{2}/champions?api_key={3}".format(region, region2, sid, api_key)
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
    try:
        profile = get_mastery_data(name[0])
        data[i,:] = profile
        print(i)
        time.sleep(1.6)
    except:
        print("an error occurred")
        pickle.dump(data, open(region+'_'+str(i)+'_diamond_profiles.p','w'))
        sys.exit()


#pickle.dump(data, open(region+'_profiles.p','w'))
pickle.dump(data, open(region+'_diamond_profiles.p','w'))
