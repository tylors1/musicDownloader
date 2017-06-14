import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import os

os.environ['SPOTIPY_CLIENT_ID']='CLIENT ID'
os.environ['SPOTIPY_CLIENT_SECRET']='SECRET CLIENT'
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost/'

username = 'USERNAME'
scope = 'user-library-read'
# scope = ''

token = util.prompt_for_user_token(username, scope)

def get_spotify_data(text_to_search, text_to_search_corrected):
	sp = spotipy.Spotify(auth=token)
	#First try text to search, if no results try text corrected
	try:
		spotify_search = sp.search(q=text_to_search, limit=1)
		# print json.dumps(convert(spotify_search), indent = 2)
		track_name = spotify_search['tracks']['items'][0]['name']
	except Exception as e: 
		print "Trying corrected search with spotify -", text_to_search_corrected
		print(e)
		try:
			if text_to_search_corrected: #if text is corrected, try the corrected text
				spotify_search = sp.search(q=text_to_search_corrected, limit=1)
				track_name = spotify_search['tracks']['items'][0]['name']
		except:
			return 
			print "Spotify Error in get_spotify_data()"
	try:
		track_id = spotify_search['tracks']['items'][0]['id']
		track_number = spotify_search['tracks']['items'][0]['track_number']
		cover_art = spotify_search['tracks']['items'][0]['album']['images'][0]['url']
		artist = spotify_search['tracks']['items'][0]['album']['artists'][0]['name']
		print "Artist -", artist
		album = spotify_search['tracks']['items'][0]['album']['name']
		print "Album -", album
		track = sp.track(track_id)
		duration = int(track['duration_ms'])/1000
	except:
		print "Couldn't get data from spotify"
		duration, track_name, track_id, track_number, cover_art, artist, album = ('',)*7
		return duration, track_name, track_id, track_number, cover_art, artist, album
	if check_unwanted_data(track_name, artist, album):
		return ('',)*7
	else:
		return duration, track_name, track_id, track_number, cover_art, artist, album

def check_unwanted_data(track_name, artist, album):
	# Found unoriginal version on spotify, clear data
	if 'karaoke' in track_name.lower() or 'karaoke' in artist.lower() or 'tribute' in track_name.lower() or 'tribute' in artist.lower() or 'tribute' in album.lower() or not track_name:
		print "Incorrect data detected, clearing terms..."
		return True
	else:
		return False
