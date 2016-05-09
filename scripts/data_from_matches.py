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

#region = 'na'

region = sys.argv[1]
#sum_ids = sys.argv[2:]

get_ids = {'br':[482762,522422,2900847,980197,664103,1210455,1519016,7281714,4520622,7764879],
           'eune':[30835511,34619107,34756594,34548067,40504926,47708236,35728787,36321134,56867645],
           'euw':[44747756,73296903,73676986,84039780,21113487,74098038,128202,37873352,47459521],
           'jp':[], #NOTE: no data exists for Japan on lolking
           'kr':[1393430,7431250,7876711,5205491,5801712],
           'lan':[155469,218300,674816,335585,523369],
           'las':[311190,135921,147196,107671,207319],
           'oce':[278081,332687,227574,229050,277369],
           'na':[34523885,32171663,46324534,35890783,53191707],
           'ru':[1260179,254634,2570126,410657,2490190],
           'tr':[6660199,1198633,11220275,9370189,4218078],
          }

sum_ids = get_ids[region]

api_key = open('key.txt','r').read().rstrip()

#sum_id = #53917147#33999121#20035307#21175578#36049629

count = 0

for sum_id in sum_ids:

    # Get list of matches from a particular summoner ID
    matches_query = "https://{0}.api.pvp.net/api/lol/{0}/v2.2/matchlist/by-summoner/{1}?rankedQueues=TEAM_BUILDER_DRAFT_RANKED_5x5&api_key={2}".format(region, sum_id, api_key)
    success = False
    while not success:
        try:
            fs = urllib2.urlopen(matches_query)
            js = json.loads(fs.read())
            time.sleep(1.5)
            success = True
        except:
            print("error occurred with match query, trying again")
            time.sleep(1.5)
            success = False
    matches = js['matches']

    # dictionary of all summoner data to be gathered
    # keys are summoner ID so duplicates overwrite automatically
    summoners = {}

    print("num matches:", len(matches))

    for m in matches:
        mid = m['matchId']
        match_query = "https://{0}.api.pvp.net/api/lol/{0}/v2.2/match/{1}?api_key={2}".format(region, mid, api_key)
        success = False
        already_failed = False
        while not success:
            try:
                f = urllib2.urlopen(match_query)
                j = json.loads(f.read())
                time.sleep(1.5) # Prevent spamming the server
                success = True
            except:
                # just end things and save here
                print("error occurred with query, trying again")
                time.sleep(1.5) # Prevent spamming the server
                if already_failed:
                    print("error occurred with query, previously failed, skipping")
                    break
                success = False
                already_failed = True
        if already_failed:
            continue
        participants = j['participants']
        ident = j['participantIdentities']
        for i,p in enumerate(participants):
            tier = p['highestAchievedSeasonTier']
            #pid = p['participantId']
            name = ident[i]['player']['summonerName']
            sid = ident[i]['player']['summonerId']
            if sid in summoners or tier != 'DIAMOND':
                continue
            summoners[sid] = [name, tier, region]
            print(name, count)
            count += 1

            #only take 1000 diamond summoners, so it isn't too large
            if count >= 1000:
                break

        #only take 1000 diamond summoners, so it isn't too large
        if count >= 1000:
            break

    #only take 1000 diamond summoners, so it isn't too large
    if count >= 1000:
        break

    
# Build names list from summoner data

names = []

for sid in summoners:
    names.append([sid, summoners[sid][0], summoners[sid][1], region])


#pickle.dump(names, open(region+'_match_test_summoners.p', 'w'))
#pickle.dump(names, open(region+'_'+str(sum_id)+'_match_summoners.p', 'w'))
pickle.dump(names, open(region+'_diamond_summoners.p', 'w'))
