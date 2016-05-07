import os
from os import curdir, sep
import json
import numpy as np
import cPickle as pickle
import os.path
import urllib2

from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash, jsonify

app = Flask(__name__)
app.config.from_object(__name__)

# trying different methods of doing the match
match_modes = ['basic', 'weighted', 'weighted2', 'weighted3', 'presquared']
match_mode = match_modes[3]

NUM_CHAMPIONS = 130
IMAGE_PREFIX = 'http://ddragon.leagueoflegends.com/cdn/5.22.3/img/champion/' #TODO: update path


region='na'
region2='na1'

api_key = open('key.txt','r').read().rstrip()
data = pickle.load(open('na_profiles.p','r'))
names = pickle.load(open('na_summoners.p', 'r'))
champs = pickle.load(open('ordered_champs.p', 'r'))
cid_to_index = pickle.load(open('cid_mapping.p','r'))

@app.route('/')
def startup():
    return render_template('index.html')

@app.route('/suggestions', methods=['POST'])
def suggestions():
    summoner_name = request.get_data()
    summoner_name = summoner_name[14:]

    response = retrieve_data(summoner_name)

    return jsonify(response)


def retrieve_data(sum_name, region='na', region2='na1'):

    clean_sum_name = sum_name.replace(" ", "").lower()

    # Get Summoner ID
    sum_id_query = "https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}".format(region, clean_sum_name, api_key)
    print(sum_id_query)
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
            'matches': matches}


"""
class SuggestServer(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):

        self.api_key = open('key.txt','r').read().rstrip()
        self.data = pickle.load(open('na_profiles.p','r'))
        self.names = pickle.load(open('na_summoners.p', 'r'))
        self.champs = pickle.load(open('ordered_champs.p', 'r'))
        self.cid_to_index = pickle.load(open('cid_mapping.p','r'))

        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
                
    def do_POST(self):
        if self.path == '/suggestions':

            content_len = int(self.headers.getheader('content-length', 0))
            summoner_name = self.rfile.read(content_len)

            # Cut out the 'summoner_name=' part
            summoner_name = summoner_name[14:]
            response = self.retrieve_data(summoner_name)
            if response is None:
              self.send_response(404)
              self.end_headers()
              return
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            json.dump(response, self.wfile)

            return

        elif self.path == "/" or self.path.endswith('.html'):
            
            #Open the static file requested and send it
            f = open(curdir + sep + self.path + '../index.html') 
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        else:
            f = open(self.path) 
            self.send_response(200)
            self.send_header('Content-type','text/css')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
    
    def do_GET(self):

        if self.path == "/":
            
            #Open the static file requested and send it
            f = open(curdir + sep + self.path + 'index.html') 
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path.endswith('.css'):
            f = open(curdir + self.path) 
            self.send_response(200)
            self.send_header('Content-type','text/css')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path.endswith('.ico'):
            f = open(curdir + self.path) 
            self.send_response(200)
            self.send_header('Content-type','text/css')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path.endswith('.html'):
            f = open(curdir + self.path) 
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path.endswith('.js'):
            f = open(curdir + self.path) 
            self.send_response(200)
            self.send_header('Content-type','text/js')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path.endswith('.png'):
            f = open(curdir + self.path) 
            self.send_response(200)
            self.send_header('Content-type','image/png')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
        elif self.path.endswith('.jpg'):
            f = open(curdir + self.path) 
            self.send_response(200)
            self.send_header('Content-type','image/jpg')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()

    def retrieve_data(self, sum_name, region='na', region2='na1'):

        clean_sum_name = sum_name.replace(" ", "").lower()

        # Get Summoner ID
        sum_id_query = "https://{0}.api.pvp.net/api/lol/{0}/v1.4/summoner/by-name/{1}?api_key={2}".format(region, clean_sum_name, self.api_key)
        print(sum_id_query)
        f = urllib2.urlopen(sum_id_query)
        j = json.loads(f.read())
        sum_id = int(j[clean_sum_name]['id'])

        # Get Mastery Data
        query = "https://{0}.api.pvp.net/championmastery/location/{1}/player/{2}/champions?api_key={3}".format(region, region2, sum_id, self.api_key)

        f = urllib2.urlopen(query)
        j = json.loads(f.read())

        user_data = np.zeros((1,NUM_CHAMPIONS))

        total_points = 0
        for champ in j:
            cid = champ['championId']
            pts = champ['championPoints']

            #convert champion id to champion index
            cindex = self.cid_to_index[cid]

            user_data[0,cindex] = pts
            total_points += pts

        user_data[0,:] /= np.sum(user_data[0,:])

        # Do matching
        if match_mode == 'basic':
            result = np.linalg.norm(self.data - user_data, axis=1)
        elif match_mode == 'weighted':
            result = np.linalg.norm(np.multiply(self.data - user_data, user_data), axis=1)
        elif match_mode == 'weighted2':
            result = np.linalg.norm(np.multiply(self.data - user_data, np.multiply(user_data, user_data)), axis=1)
        elif match_mode == 'weighted3':
            result = np.linalg.norm(np.multiply(self.data - user_data, np.multiply(np.multiply(user_data, user_data), user_data)), axis=1)
        elif match_mode == 'presquared':
            result = np.linalg.norm(self.data - user_data, axis=1)

        indices = np.argsort(result)
        index = np.argmin(result)

        matches = []
        #names : id, name, league, region
        for i in indices[:5]:
            matches.append([self.names[i]])

        return {'summoner_name':sum_name,
                'matches': matches}



def main():
    try:
        # you can specify any port you want by changing '8000'
        server = HTTPServer(('', 8000), SuggestServer)
        print 'running httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()
"""
if __name__ == '__main__':
    app.run()