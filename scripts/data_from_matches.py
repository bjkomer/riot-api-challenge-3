# Get summoner data by going through match history
# For getting data on Diamond and other players
import numpy as np
import cPickle as pickle
import sys
import json
import urllib2
import time

# Open an IPython session if an exception is found
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)

region = 'na'
api_key = open('key.txt','r').read().rstrip()

sum_id = 36049629#53917147#33999121#20035307#21175578#36049629

# Get list of matches from a particular summoner ID
matches_query = "https://{0}.api.pvp.net/api/lol/{0}/v2.2/matchlist/by-summoner/{1}?rankedQueues=TEAM_BUILDER_DRAFT_RANKED_5x5&api_key={2}".format(region, sum_id, api_key)

fs = urllib2.urlopen(matches_query)
js = json.loads(fs.read())
matches = js['matches']

print(matches)

# dictionary of all summoner data to be gathered
# keys are summoner ID so duplicates overwrite automatically
summoners = {}

test_count = 0
print("num matches:", len(matches))

for m in matches:
    mid = m['matchId']
    match_query = "https://{0}.api.pvp.net/api/lol/{0}/v2.2/match/{1}?api_key={2}".format(region, mid, api_key)
    try:
        f = urllib2.urlopen(match_query)
        j = json.loads(f.read())
    except:
        # just end things and save here
        print("error occurred with query, exiting and saving results")
        break
    participants = j['participants']
    ident = j['participantIdentities']
    for i,p in enumerate(participants):
        tier = p['highestAchievedSeasonTier']
        #pid = p['participantId']
        name = ident[i]['player']['summonerName']
        sid = ident[i]['player']['summonerId']
        summoners[sid] = [name, tier, region]
        print(name, test_count)
    time.sleep(1.5) # Prevent spamming the server
    test_count += 1

    """
    #TEMP FIXME for testing
    if test_count == 10:
        break
    """
    
# Build names list from summoner data

names = []

for sid in summoners:
    names.append([sid, summoners[sid][0], summoners[sid][1], region])


#pickle.dump(names, open(region+'_match_test_summoners.p', 'w'))
pickle.dump(names, open(region+'_'+str(sum_id)+'_match_summoners.p', 'w'))
