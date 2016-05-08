# combine pickled mastery profile data into a single file
import numpy as np
import cPickle as pickle
import sys
import json
import urllib2
import time

# Mastery Profiles

input_pickles = ['na_profiles.p', 'na_diamond_profiles.p']

output_pickle = 'na_combined_profiles.p'

data = []

for ip in input_pickles:
    values = pickle.load(open(ip, 'r'))
    for v in values:
        data.append(v)

pickle.dump(data, open(output_pickle, 'w'))


# Names

input_pickles = ['na_summoners.p', 'na_diamond_summoners.p']

output_pickle = 'na_combined_summoners.p'

data = []

for ip in input_pickles:
    values = pickle.load(open(ip, 'r'))
    for v in values:
        data.append(v)

pickle.dump(data, open(output_pickle, 'w'))
