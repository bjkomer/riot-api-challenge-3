import numpy as np
import cPickle as pickle

NUM_CHAMPIONS = 130
NUM_SUMMONERS = 1000

np.random.seed(13)

# Ordered normalized mastery profiles
data = np.zeros((NUM_SUMMONERS, NUM_CHAMPIONS))

# Ordered summoner IDs and names
names = []#np.zeros((NUM_SUMMONERS, 2))

#generate random dataset
for s in range(NUM_SUMMONERS):
    for c in range(NUM_CHAMPIONS):
        data[s,c] = np.random.random()
    # normalize
    data[s,:] /= np.sum(data[s,:])
    names.append([s, "Summoner"+str(s)])

#print(data)
#print(names)

user_data = np.zeros((1,NUM_CHAMPIONS))


for c in range(NUM_CHAMPIONS):
    user_data[0,c] = np.random.random()
user_data[0,:] /= np.sum(user_data[0,:])

result = np.linalg.norm(data - user_data, axis=1)
#TODO: possibly weight the norm result by the user's data
#      this way champs they play more are more important to match

print(result.shape)
index = np.argmin(result)
print(index)

print(data[index,:5])
print(user_data[0,:5])
print(data[0,:5])
print(data[1,:5])
print(data[2,:5])

pickle.dump(data, open('test_profiles.p','w'))
pickle.dump(names, open('test_summoners.p', 'w'))
