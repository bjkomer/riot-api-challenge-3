# get all data for master and challenger players
#TODO: possibly combine regions for more results

import numpy as np
import cPickle as pickle
import sys
import json
import urllib2

#NUM_SUMMONERS = 1000

region = 'na'
api_key = open('key.txt','r').read().rstrip()

c_query = "https://{0}.api.pvp.net/api/lol/{0}/v2.5/league/challenger?type=RANKED_SOLO_5x5&api_key={1}".format(region, api_key)
m_query = "https://{0}.api.pvp.net/api/lol/{0}/v2.5/league/master?type=RANKED_SOLO_5x5&api_key={1}".format(region, api_key)

m_f = urllib2.urlopen(m_query)
m_j = json.loads(m_f.read())
m_s = m_j['entries']

c_f = urllib2.urlopen(c_query)
c_j = json.loads(c_f.read())
c_s = c_j['entries']

NUM_SUMMONERS = len(m_s) + len(c_s)

names = []
for i in range(len(c_s)):
    names.append([c_s[i]['playerOrTeamId'], c_s[i]['playerOrTeamName'], 'Challenger', region])

for i in range(len(m_s)):
    names.append([m_s[i]['playerOrTeamId'], m_s[i]['playerOrTeamName'], 'Master', region])

pickle.dump(names, open(region+'_summoners.p', 'w'))
