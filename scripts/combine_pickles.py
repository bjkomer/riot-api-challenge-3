# combine pickled data into a single file
import numpy as np
import cPickle as pickle
import sys
import json
import urllib2
import time

input_pickles = ['na_20035307_match_summoners.p', 'na_21175578_match_summoners.p', 
                 'na_33999121_match_summoners.p', 'na_53917147_match_summoners.p',]
                 #'na_summoners.p']

possible_tiers = ['DIAMOND']
#possible_tiers = ['DIAMOND', 'MASTER', 'CHALLENGER']

output_pickle = 'na_diamond_summoners.p'

# use dictionary so duplicates handled nicely
summoners = {}
for in_pickle in input_pickles:
    data = pickle.load(open(in_pickle, 'r'))
    for d in data:
        if d[2].upper() in possible_tiers:
            summoners[d[0]] = [d[1], d[2], d[3]]


names = []

for sid in summoners:
    names.append([sid, summoners[sid][0], summoners[sid][1], summoners[sid][2]])


pickle.dump(names, open(output_pickle, 'w'))


