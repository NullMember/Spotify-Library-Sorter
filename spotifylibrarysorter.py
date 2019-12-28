import sys
import spotipy
import spotipy.util as util
import json
import os
from tqdm import tqdm

login_choices = ['Use last user', 'Enter username']
playlist_choices = ['Show user playlists', 'Get songs from file', 'Search playlist']
after_playlist_choices = ['Print playlist', 'Print average', 'Save playlist to file', 'Sort playlist', 'Make copy of this playlist', 'Go back to playlist selection']
sort_choices = ['name', 'artist', 'album', 'popularity', 'duration_ms', 'key', 'mode', 'time_signature', 'acousticness',  'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
sort_dir = ['Ascending', 'Descending']
save_choices = ['Print playlist', 'Save playlist to file', 'Make copy of this playlist', 'Do nothing', 'Save this order to current playlist', 'Merge with...']
end_choices = ['Go back to login', 'Go back to playlist selection', 'Resort playlist', 'Close the program']
keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
modes = ['Major', 'Minor']

login_choice = -1
playlist_choice = -1
after_playlist_choice = -1
sort_choice = -1
save_choice = -1
end_choice = -1
temp_choice = -1

# You can get these from developer.spotify.com
spotipy_client_id = 'your_client_id'                # Enter your application's spotify client id 
spotipy_client_secret = 'your_client_secret'        # Enter your application's spotify client secret
spotipy_redirect_uri = 'your_callback_uri'          # Enter your application's spotify redirect uri

scope = 'user-library-read playlist-modify-public user-read-private user-read-email'
me_id = ''
playlist_owner_id = ''
playlist_id = ''
playlist_total_tracks = 0
playlist_tracks = {}
playlist_search_limit = 50

def show_tracks(tracks):
    print("{0:3s} {1:24s} {2:24s} {3:24s} {4:3s} {5:8s} {6:3s} {7:5s} {8:3s} {9:8s} {10:8s} {11:8s} {12:8s} {13:8s} {14:8s} {15:8s} {16:8s} {17:6s}".format(\
    "Ord",\
    "Title",\
    "Artist",\
    "Album",\
    "Pop",\
    "Duration",\
    "Key",\
    "Mode ",\
    "Sig",\
    "Acoustic",\
    "Danceabi",\
    "Energy  ",\
    "Instrume",\
    "Liveness",\
    "Loudness",\
    "Speechin",\
    "Valence ",\
    "Tempo "))
    for i, key in enumerate(tracks.keys()):
        print("{0:3d} {1:24s} {2:24s} {3:24s} {4:3d} {5:8d} {6:3s} {7:5s} {8:3d} {9:1.6f} {10:1.6f} {11:1.6f} {12:1.6f} {13:1.6f} {14:4.3f} {15:1.6f} {16:1.6f} {17:3.2f}".format(\
        i,\
        tracks[key]['name'][0:24],\
        tracks[key]['album'][0:24],\
        tracks[key]['artist'][0:24],\
        tracks[key]['popularity'],\
        tracks[key]['duration_ms'],\
        keys[tracks[key]['key']],\
        modes[tracks[key]['mode']],\
        tracks[key]['time_signature'],\
        tracks[key]['acousticness'],\
        tracks[key]['danceability'],\
        tracks[key]['energy'],\
        tracks[key]['instrumentalness'],\
        tracks[key]['liveness'],\
        tracks[key]['loudness'],\
        tracks[key]['speechiness'],\
        tracks[key]['valence'],\
        tracks[key]['tempo']))

def getfeatures(tracks):
    list_tracks = {}
    track_ids = []
    for i, item in enumerate(tracks['items']):
        track_ids.append(item['track']['id'])
    features = sp.audio_features(track_ids)
    for i, item in enumerate(tracks['items']):
        track_id = item['track']['id']
        list_tracks[track_id] = {}
        list_tracks[track_id]['name'] = item['track']['name']
        list_tracks[track_id]['artist'] = item['track']['artists'][0]['name']
        list_tracks[track_id]['album'] = item['track']['album']['name']
        list_tracks[track_id]['popularity'] = item['track']['popularity']
        list_tracks[track_id]['duration_ms'] = features[i]['duration_ms']
        list_tracks[track_id]['key'] = features[i]['key']
        list_tracks[track_id]['mode'] = features[i]['mode']
        list_tracks[track_id]['time_signature'] = features[i]['time_signature']
        list_tracks[track_id]['acousticness'] = features[i]['acousticness']
        list_tracks[track_id]['danceability'] = features[i]['danceability']
        list_tracks[track_id]['energy'] = features[i]['energy']
        list_tracks[track_id]['instrumentalness'] = features[i]['instrumentalness']
        list_tracks[track_id]['liveness'] = features[i]['liveness']
        list_tracks[track_id]['loudness'] = features[i]['loudness']
        list_tracks[track_id]['speechiness'] = features[i]['speechiness']
        list_tracks[track_id]['valence'] = features[i]['valence']
        list_tracks[track_id]['tempo'] = features[i]['tempo']
    return list_tracks

def get_songs_in_playlist(_playlist_owner_id, _playlist_id, _playlist_total_tracks):
    playlist_tracks = {}
    tracks = []
    print('Getting songs from playlist...')
    for i in tqdm(range(int((_playlist_total_tracks / 100) + 1))):
        tracks.append(sp.user_playlist_tracks(_playlist_owner_id, _playlist_id, offset = 100 * i, limit = 100))
        playlist_tracks.update(getfeatures(tracks[i]))
    return playlist_tracks

def get_average(tracks):
    average = {}
    print('Calculating average values of tracks features...')
    _keys = []
    _modes = []
    _time_signatures = []
    avg_popularity = 0.
    avg_duration_ms = 0.
    avg_acousticness = 0.
    avg_danceability = 0.
    avg_energy = 0.
    avg_instrumentalness = 0.
    avg_liveness = 0.
    avg_loudness = 0.
    avg_speechiness = 0.
    avg_valence = 0.
    avg_tempo = 0.
    tracks_len = len(tracks.keys()) - 1
    for key in tqdm(tracks.keys()):
        avg_popularity = avg_popularity + tracks[key]['popularity']
        avg_duration_ms = avg_duration_ms + tracks[key]['duration_ms']
        _keys.append(tracks[key]['key'])
        _modes.append(tracks[key]['mode'])
        _time_signatures.append(tracks[key]['time_signature'])
        avg_acousticness = avg_acousticness + tracks[key]['acousticness']
        avg_danceability = avg_danceability + tracks[key]['danceability']
        avg_energy = avg_energy + tracks[key]['energy']
        avg_instrumentalness = avg_instrumentalness + tracks[key]['instrumentalness']
        avg_liveness = avg_liveness + tracks[key]['liveness']
        avg_loudness = avg_loudness + tracks[key]['loudness']
        avg_speechiness = avg_speechiness + tracks[key]['speechiness']
        avg_valence = avg_valence + tracks[key]['valence']
        avg_tempo = avg_tempo + tracks[key]['tempo']
    average['popularity'] = int(avg_popularity / tracks_len)
    average['duration_ms'] = int(avg_duration_ms / tracks_len)
    average['key'] = max(set(_keys), key = _keys.count)
    average['mode'] = max(set(_modes), key = _modes.count)
    average['time_signature'] = max(set(_time_signatures), key = _time_signatures.count)
    average['acousticness'] = avg_acousticness / tracks_len
    average['danceability'] = avg_danceability / tracks_len
    average['energy'] = avg_energy / tracks_len
    average['instrumentalness'] = avg_instrumentalness / tracks_len
    average['liveness'] = avg_liveness / tracks_len
    average['loudness'] = avg_loudness / tracks_len
    average['speechiness'] = avg_speechiness / tracks_len
    average['valence'] = avg_valence / tracks_len
    average['tempo'] = avg_tempo / tracks_len
    return average

def show_average(average):
    print("{0:1d} {1:3s} {2:8s} {3:3s} {4:5s} {5:3s} {6:8s} {7:8s} {8:8s} {9:8s} {10:8s} {11:8s} {12:8s} {13:8s} {14:6s}".format(0,\
    "Pop",\
    "Duration",\
    "Key",\
    "Mode ",\
    "Sig",\
    "Acoustic",\
    "Danceabi",\
    "Energy  ",\
    "Instrume",\
    "Liveness",\
    "Loudness",\
    "Speechin",\
    "Valence ",\
    "Tempo "))
    print("{0:1d} {1:3d} {2:8d} {3:3s} {4:5s} {5:3d} {6:1.6f} {7:1.6f} {8:1.6f} {9:1.6f} {10:1.6f} {11:4.3f} {12:1.6f} {13:1.6f} {14:3.2f}".format(0,\
        average['popularity'],\
        average['duration_ms'],\
        keys[average['key']],\
        modes[average['mode']],\
        average['time_signature'],\
        average['acousticness'],\
        average['danceability'],\
        average['energy'],\
        average['instrumentalness'],\
        average['liveness'],\
        average['loudness'],\
        average['speechiness'],\
        average['valence'],\
        average['tempo']))

def add_tracks_to_playlist(tracks, _owner_id, _playlist_id):
    new_playlist_tracks = []
    for key in tracks.keys():
        new_playlist_tracks.append(key)
    print('Adding tracks to playlist')
    for i in tqdm(range(int((len(new_playlist_tracks) / 100) + 1))):
        sp.user_playlist_add_tracks(_owner_id, _playlist_id, new_playlist_tracks[(i * 100):((i + 1) * 100)])
    print('Added all tracks to playlist')

def search_playlist(query):
    return sp.search(query, limit=playlist_search_limit, offset=0, type='playlist')

def ignore_the(_str):
    if _str.lower()[:4] == 'the ':
        return _str[4:]
    else:
        return _str

def sort_tracks(tracks, sortby, reverse=False):
    _sorter = []
    if (sortby == 'name') or (sortby == 'artist') or (sortby == 'album'):
        for key in tracks.keys():
            _sorter.append((ignore_the(tracks[key][sortby]), key))
    else:
        for key in tracks.keys():
            _sorter.append((tracks[key][sortby], key))
    _sorted = sorted(_sorter, reverse = reverse)
    _tracks = {}
    for val, key in _sorted:
        _tracks[key] = tracks[key]
    return _tracks

if __name__ == "__main__":
    if os.path.exists('lastuser.json'):
        with open('lastuser.json') as f:
            username = json.load(f)['last-user']
    else:
        username = -1
    while 1:
        if login_choice == -1:
            temp_choice = -1
            for i in range(len(login_choices)):
                print(i, login_choices[i])
            while ((login_choice < 0) or (login_choice >= len(login_choices))):
                login_choice = int(input("Select login method: "))
                print('')
            if login_choice == 0:
                if username == -1:
                    print('No last known username')
                    login_choice = -1
                    continue
                else:
                    token = util.prompt_for_user_token(username, scope, spotipy_client_id, spotipy_client_secret, spotipy_redirect_uri)
            if login_choice == 1:
                username = input("Enter your spotify username or email: ")
                print('')
                token = util.prompt_for_user_token(username, scope, spotipy_client_id, spotipy_client_secret, spotipy_redirect_uri)
            if token:
                with open('lastuser.json', 'w') as f:
                    json.dump({'last-user': username}, f, indent = 4)
                sp = spotipy.Spotify(auth=token)
                me_id = sp.current_user()['id']
            else:
                print("Error while getting token!")
                login_choice = -1
                continue
        if playlist_choice == -1:
            temp_choice = -1
            for i in range(len(playlist_choices)):
                print(i, playlist_choices[i])
            while ((playlist_choice < 0) or (playlist_choice >= len(playlist_choices))):
                playlist_choice = int(input("Select playlist method: "))
                print('')
            if playlist_choice == 0:
                playlists = sp.current_user_playlists()
                if playlists['total']:
                    for i, item in enumerate(playlists['items']):
                        print(str(i), item['name'])
                    while (temp_choice < 0) or (temp_choice >= len(playlists['items'])):
                        temp_choice = int(input("Select playlist: "))
                        print('')
                    playlist_tracks = get_songs_in_playlist(playlists['items'][temp_choice]['owner']['id'], playlists['items'][temp_choice]['id'], playlists['items'][temp_choice]['tracks']['total'])
                    playlist_owner_id = playlists['items'][temp_choice]['owner']['id']
                    playlist_id = playlists['items'][temp_choice]['id']
                else:
                    print("This user has no playlist")
                    playlist_choice = -1
                    continue
            if playlist_choice == 1:
                filepath = input("Enter path of json file: ")
                print('')
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        playlist_tracks = json.load(f)
                else:
                    print('File not found!')
                    playlist_choice = -1
                    continue
            if playlist_choice == 2:
                search_query = input('Search playlist: ')
                print('')
                playlists = search_playlist(search_query)
                if playlists['playlists']['total']:
                    for i, item in enumerate(playlists['playlists']['items']):
                        print(str(i), item['name'], 'by', item['owner']['display_name'])
                    while ((temp_choice < 0) or (temp_choice >= len(playlist_choices))):
                        temp_choice = int(input("Select playlist: "))
                        print('')
                    playlist_tracks = get_songs_in_playlist(playlists['playlists']['items'][temp_choice]['owner']['id'], playlists['playlists']['items'][temp_choice]['id'], playlists['playlists']['items'][temp_choice]['tracks']['total'])
                    playlist_owner_id = playlists['playlists']['items'][temp_choice]['owner']['id']
                    playlist_id = playlists['playlists']['items'][temp_choice]['id']
                else:
                    print('No playlist found')
                    playlist_choice = -1
                    continue
        if after_playlist_choice == -1:
            temp_choice = -1
            for i in range(len(after_playlist_choices)):
                print(i, after_playlist_choices[i])
            while ((after_playlist_choice < 0) or (after_playlist_choice >= len(after_playlist_choices))):
                after_playlist_choice = int(input("What to do: "))
                print('')
            if after_playlist_choice == 0:
                show_tracks(playlist_tracks)
                after_playlist_choice = -1
                continue
            if after_playlist_choice == 1:
                show_average(get_average(playlist_tracks))
                after_playlist_choice = -1
                continue
            if after_playlist_choice == 2:
                filename = input('Enter filename: ')
                print('')
                with open(filename + '.json', 'w') as f:
                    json.dump(playlist_tracks, f, indent = 4)
                after_playlist_choice = -1
                continue
            if after_playlist_choice == 3:
                pass
            if after_playlist_choice == 4:
                playlist_name = input('Enter a name for playlist: ')
                print('')
                playlist_id = sp.user_playlist_create(me_id, playlist_name)['id']
                playlist_owner_id = me_id
                add_tracks_to_playlist(playlist_tracks, playlist_owner_id, playlist_id)
                after_playlist_choice = -1
                continue
            if after_playlist_choice == 5:
                after_playlist_choice = -1
                playlist_choice = -1
                continue
        if sort_choice == -1:
            temp_choice = -1
            for i in range(len(sort_choices)):
                print(i, sort_choices[i])
            while ((sort_choice < 0) or (sort_choice >= len(sort_choices))):
                sort_choice = int(input("Sort playlist by: "))
                print('')
            for i in range(len(sort_dir)):
                print(i, sort_dir[i])
            while ((temp_choice < 0) or (temp_choice >= len(sort_dir))):
                temp_choice = int(input("Sort order: "))
                print('')
            temp_choice = temp_choice == 1
            playlist_tracks = sort_tracks(playlist_tracks, sort_choices[sort_choice], temp_choice)
        if save_choice == -1:
            temp_choice = -1
            for i in range(len(save_choices)):
                print(i, save_choices[i])
            while ((save_choice < 0) or (save_choice >= len(save_choices))):
                save_choice = int(input("What to do: "))
                print('')
            if save_choice == 0:
                show_tracks(playlist_tracks)
                save_choice = -1
                continue
            if save_choice == 1:
                filename = input('Enter filename: ')
                print('')
                with open(filename + '.json', 'w') as f:
                    json.dump(playlist_tracks, f, indent = 4)
                save_choice = -1
                continue
            if save_choice == 2:
                playlist_name = input('Enter a name for playlist: ')
                print('')
                playlist_id = sp.user_playlist_create(me_id, playlist_name)['id']
                playlist_owner_id = me_id
                add_tracks_to_playlist(playlist_tracks, playlist_owner_id, playlist_id)
                save_choice = -1
                continue
            if save_choice == 3:
                continue
            if save_choice == 4:
                if me_id == playlist_owner_id:
                    sp.user_playlist_replace_tracks(playlist_owner_id, playlist_id, [])
                    add_tracks_to_playlist(playlist_tracks, playlist_owner_id, playlist_id)
                    continue
                else:
                    print('You don\'t have permission for that')
                    save_choice = -1
                    continue
            if save_choice == 5:
                playlists = sp.current_user_playlists()
                if playlists['total']:
                    for i, item in enumerate(playlists['items']):
                        print(str(i), item['name'])
                    while (temp_choice < 0) or (temp_choice >= len(playlists['items'])):
                        temp_choice = int(input("Select playlist: "))
                        print('')
                    playlist_owner_id = playlists['items'][temp_choice]['owner']['id']
                    playlist_id = playlists['items'][temp_choice]['id']
                    add_tracks_to_playlist(playlist_tracks, playlist_owner_id, playlist_id)
                else:
                    print("This user has no playlist")
                    save_choice = -1
                    continue
        if end_choice == -1:
            temp_choice = -1
            for i in range(len(end_choices)):
                print(i, end_choices[i])
            while ((end_choice < 0) or (end_choice >= len(end_choices))):
                end_choice = int(input("What to do: "))
                print('')
            if end_choice == 0:
                login_choice = -1
                playlist_choice = -1
                after_playlist_choice = -1
                sort_choice = -1
                save_choice = -1
                end_choice = -1
                continue
            if end_choice == 1:
                playlist_choice = -1
                after_playlist_choice = -1
                sort_choice = -1
                save_choice = -1
                end_choice = -1
                continue
            if end_choice == 2:
                sort_choice = -1
                save_choice = -1
                end_choice = -1
                continue
            if end_choice == 3:
                sys.exit(0)