from flask import Flask, request, render_template, session, redirect

app = Flask(__name__)

app.config["SECRET_KEY"] = "7}%u9(_!>8p3;!B9N'U7CQP|lj>=Uw"

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from random import *

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="be77cd101b3f4241a9f0a11e910d07c5",
                                                           client_secret="5d74b80dea844e8aad672355adf232f1"))



@app.route('/')
def my_form():
	session['round'] = True
	session['list'] = []
	return render_template("home.html")



@app.route('/', methods=['POST'])
def my_form_post():
	if session['round'] == True:
		session['round'] = False
		artist1_str = request.form['text1']
		if get_artist(artist1_str) == None:
			return render_template("inputerror.html", artist1 = artist1_str)
		artist1_id = get_artist(artist1_str)
		session['list'].append(artist1_id)
		artist2_id = reponse_par_pop(artist1_id,session['list'])
		session['list'].append(artist2_id)
		artist2_str = sp.artist(artist2_id)['name']
		session['artist'] = artist2_id
		return render_template("default.html", artist1 = artist1_str, artist2 = artist2_str)
	else:
		artist1_str = request.form['text1']
		if get_artist(artist1_str) == None:
			return render_template("inputerror.html", artist1 = artist1_str)
		artist1_id = get_artist(artist1_str)
		if (artist1_id in session['list']):
			return render_template("gameover.html", artist1 = artist1_str)
		artist2_id = session['artist']
		artist2_str = sp.artist(artist2_id)['name']
		if not ont_feate(artist1_id, artist2_id):
			return render_template("gameover2.html", artist1 = artist1_str, artist2 = artist2_str)
		session['list'].append(artist1_id)
		artist2_id = reponse_par_pop(artist1_id, session['list'])
		session['list'].append(artist2_id)
		artist2_str = sp.artist(artist2_id)['name']
		session['artist'] = artist2_id
		return render_template("default.html", artist1 = artist1_str, artist2 = artist2_str)



# Fonction qui prend en argument le nom de l'artiste
# et qui renvoie l'identifiant de l'artiste correspondant

def get_artist(artist_name):
    results = sp.search(q='artist:' + artist_name, type='artist', market='FR')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]['id']
    else:
        return None



# Fonction qui prend en argument l'identifiant spotify d'un artiste
# et qui renvoie la liste des identifiants de tous les artistes ayant collaboré avec ce dernier

def get_featurings(artist_id, black_list):
    artist = sp.artist(artist_id)
    featurings_list = []
    for x in range(2):
        results = sp.search(artist['name'], limit=50, offset=50*x, type='track', market='FR')
        songs = results['tracks']['items']
        n = len(songs)
        c = 0
        for i in range(n-1):
            nombre_artiste = len(songs[i]['artists'])
            erreur = True
            for j in range(nombre_artiste):
                if songs[i]['artists'][j]['id'] != artist_id:
                    c += 1
                    if (songs[i]['artists'][j]['id'] not in black_list):
                        featurings_list.append(songs[i]['artists'][j]['id'])
                else:
                    erreur = False
            if erreur:
                for k in range(nombre_artiste):
                    featurings_list.pop()
    featurings_list_sans_doublons = []
    taille = len(featurings_list)
    for i in range(0, taille):
        if featurings_list[i] in featurings_list_sans_doublons:
            pass
        else:
            featurings_list_sans_doublons.append(featurings_list[i])
    return featurings_list_sans_doublons



# Fonction qui prend en argument l'identifiant spotify d'un artiste
# et qui renvoie l'identifiant de l'artiste le moins connu parmi ceux avec qui le premier a collaboré

def reponse_par_pop(artist_id, black_list):
    L = get_featurings(artist_id, black_list)
    n = len(L)
    indice_min = 0
    for i in range(n):
        if sp.artist(L[i])['popularity']<sp.artist(L[indice_min])['popularity']:
            if sp.artist(L[i])['popularity'] >= randint(40, 70):
                indice_min = i
    return L[indice_min]



# Fonction qui prend en argument les identifiants spotify de deux artistes
# et qui renvoie True s'ils ont déjà featé et False sinon

def ont_feate(artist1_id, artist2_id):
    return artist2_id in get_featurings(artist1_id, [])



if __name__ == '__main__':
    app.run()
