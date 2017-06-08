from __future__ import unicode_literals
import youtube_dl
import urllib
import urllib2
import json
import collections
import sys
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import pprint
import os
import eyed3
import wikipedia
import re
import difflib
import unidecode
import codecs
import time


os.environ['SPOTIPY_CLIENT_ID']='client_id goes here'
os.environ['SPOTIPY_CLIENT_SECRET']='secret goes here'
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost/'

client_credentials_manager = SpotifyClientCredentials(client_id='60e52fd7ef4849568a7c057416d33554', client_secret='35bf0fd6643d432c9f0f906c2860f6a3')
username = 'username here'
scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope)

# Keep track failed meta searches
open('incomplete_meta.txt', 'w').close()
open('unable_to_download.txt', 'w').close()
incomplete_meta = []
unable_to_download = []

### HELPER FUNCTIONS ###
def convert(data): #converts unicode
    if isinstance(data, basestring):
        # return  u''.join(data).encode('utf-8').strip()
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

def output_to_file(data): #if outputting soup, append .prettify() to soup variable => soupy.prettify()
	text_file = open("Output.txt", "w")
	try:
		text_file.write(data.encode("utf-8"))
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)
		text_file.write(convert(data))
	text_file.close()

def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]

def get_sec(time_str):
	if len(time_str) < 6:
	    m, s = time_str.split(':')
	    return int(m) * 60 + int(s)
	else:
	    h, m, s = time_str.split(':')
    	return int(h) * 3600 + int(m) * 60 + int(s)

### ###
def get_da_music(text_to_search):
	text_to_search, text_to_search_corrected = correct_search(text_to_search)
	duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = get_meta_data(text_to_search, text_to_search_corrected)
	download_url = get_youtube_url(track_name, artist)
	file_name = youtube_download(track_name, download_url, artist)
	fix_tags(file_name, [duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres])

def get_da_music_no_file(text_to_search):
	text_to_search, text_to_search_corrected = correct_search(text_to_search)
	duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = get_meta_data(text_to_search, text_to_search_corrected)
	download_url = get_youtube_url(track_name, artist)
	print
	print
	manual_entry(download_url)

def manual_entry(download_url):
	soup = BeautifulSoup(urllib2.urlopen(download_url).read(), "html.parser")
	title = soup.title.text[:-10]
	duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = get_meta_data(title, "")
	print "Track name:", track_name + '\n', "Artist:", artist + '\n', "Album:", album + '\n', "Album date:", album_date + '\n', "Genre: ", genres
	print "Edit tag details? (y/n)"
	entry = raw_input()
	confirm = False
	if not entry.strip() or entry.strip().lower() == 'y':
		while not confirm:
			track_name, artist, album, album_date, genres = new_tags(track_name, artist, album, album_date, genres)
			print "Track name:", track_name + '\n', "Artist:", artist + '\n', "Album:", album + '\n', "Album date:", album_date + '\n', "Genre: ", genres
			print "Confirm? (y/n)"
			entry = raw_input()
			if not entry.strip() or entry.strip().lower() == 'y':
				confirm = True
	else:
		duration, track_id, track_number, cover_art, artist, album, album_date, genres = ('',)*8
		track_name = title
	file_name = youtube_download(track_name, download_url, artist)
	fix_tags(file_name, [duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres])

def new_tags(track_name, artist, album, album_date, genres):
	print "Enter nothing to keep found details"
	print "Track name:", track_name
	track_name = enter_details(track_name)
	print "Artist:", artist
	artist = enter_details(artist)
	print "Album:", album
	artist = enter_details(album)
	print "Album date:", album_date
	album_date = enter_details(album_date)
	print "Genre:", genres
	genre = enter_details(genres)
	return track_name, artist, album, album_date, genres

def enter_details(variable):
	entry = raw_input()
	if entry.strip():
		return entry
	else:
		return variable
	

### YOUTUTBE ###
# piggyback youtube's spellchecker & query corrector
def correct_search(text_to_search): 
	url = "https://www.youtube.com/results?search_query=" + urllib.quote(convert(text_to_search)) + "&sp=EgIgAQ%253D%253D"
	soup = BeautifulSoup(urllib2.urlopen(url).read(), "html.parser").prettify()
	text_to_search_corrected = ""
	try:
		text_to_search_corrected = soup.find('span', attrs={"class":"spell-correction-corrected"}).find_next('a').text
		print "Searching instead for -", text_to_search_corrected
	except Exception as e:
		# print(e)
		print "Searching for -", text_to_search
	return text_to_search, text_to_search_corrected

#URLs from YouTube search
def get_youtube_search_list(query):
	print "Searching YouTube for -", query
	query = urllib.quote(convert(query))
	url = "https://www.youtube.com/results?search_query=" + query + "&sp=EgIgAQ%253D%253D"
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, "html.parser")
	output_to_file(soup)
	vid_list = []
	duration_list = []
	title_list = []
	channel_list = []
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
	    vid_list.append('https://www.youtube.com'.encode('UTF8') + vid['href'].encode('UTF8'))
	# print "Found".encode('UTF8'), len(vid_list), "urls".encode('UTF8')
	for time in soup.findAll(attrs={'class':'video-time'}):
		duration_list.append(get_sec(time.text.encode('UTF8')))
	for title in soup.findAll(attrs={'aria-describedby':re.compile('description-id')}):
		title_list.append(title.text.encode('UTF8'))
	for channel in soup.findAll(attrs={'class':'yt-lockup-byline '}):
		channel_list.append(channel.text)
	# print "Comparing".encode('UTF8'), len(duration_list), "durations".encode('UTF8')
	search_list = zip(vid_list, duration_list, title_list, channel_list)
	return search_list

def get_youtube_url(track_name, artist):
	count = 0
	# Try to find YouTube's Topic Channel for the track
	search_list = get_youtube_search_list(track_name + " " + artist + " topic") # urls, durations, titles, channels
	for item in search_list:
		count += 1
		if "Topic" in item[3] and track_name.lower() in item[2].lower() and "live" not in item[2].lower():
			if count > 2:
				incomplete_meta.append(artist + " " + track_name + '\n')
				with open("incomplete_meta.txt", "a") as myfile:
					myfile.write(artist + " " + track_name + '\n')
			return item[0]
	# No topic channel was found, try other search
	search_list = get_youtube_search_list(track_name + " " + artist) # urls, durations, titles, channels
	for item in search_list:
		if "live" not in item[2].lower() and "karaoke" not in item[2].lower():
			incomplete_meta.append(artist + " " + track_name + '\n')
			with open("incomplete_meta.txt", "a") as myfile:
				myfile.write(artist + " " + track_name + '\n')
			return item[0]

	return ""

# Youtube Download & Convert
def youtube_download(track_name, url, artist):
	print "Downloading and converting..."
	if not artist:
		file_name = str(track_name)
	else:
		file_name = str(artist) + ' - ' + str(track_name)
	print file_name
	file_name = unidecode.unidecode(re.sub('[\\\\/:*?"<>|]', '', file_name)).rstrip()
	command_tokens = [
	    'youtube-dl',
	    '--no-warnings',
	    '--extract-audio',
	    '--audio-format mp3',
	    '--audio-quality 0',
	    '--output', '"' + file_name + '.%(ext)s' + '"',
	    url]

	command_tokens.insert(1, '-q')
	command = ' '.join(command_tokens)
	os.system(command)
	return file_name

### META DATA HANDLING ###
#Attempts spotify, then wikipedia, then musicbrainz with selenium to get metadata
def get_meta_data(text_to_search, text_to_search_corrected):
	duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = ('',)*9
	duration, track_name, track_id, track_number, cover_art, artist, album = get_spotify_data(text_to_search, text_to_search_corrected)
	# Found unoriginal version on spotify, clear data
	if 'karaoke' in track_name.lower() or 'karaoke' in artist.lower() or 'tribute' in track_name.lower() or 'tribute' in artist.lower() or not track_name:
		print "Incorrect data from spotify detected, clearing terms..."
		duration, track_id, track_number, cover_art, artist, album, album_date, genres = ('',)*8
		#Set track name equal to text to search and add to no meta list
		if text_to_search_corrected:
			track_name = text_to_search_corrected
		else:
			track_name = text_to_search
		incomplete_meta.append(track_name + '\n')
		with open("incomplete_meta.txt", "a") as myfile:
			myfile.write(track_name + '\n')
	else:
		get_wikipedia_data(track_name, artist, album)

	# get_musicbrainz_data(track_name + " " + artist)

	return duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres

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
	# print json.dumps(convert(spotify_search), indent = 2)
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
		incomplete_meta.append(text_to_search + '\n')
		with open("incomplete_meta.txt", "a") as myfile:
			myfile.write(text_to_search + '\n')
		duration, track_name, track_id, track_number, cover_art, artist, album = ('',)*7
		if text_to_search_corrected:
			track_name = text_to_search_corrected
		else:
			track_name = text_to_search
		return duration, track_name, track_id, track_number, cover_art, artist, album

	# raise ValueError
	return convert([duration, track_name, track_id, track_number, cover_art, artist, album])

def get_wikipedia_data(track_name, artist, text_to_search):
	album_date = ""
	genre = ""
	soup = ""
	found = False
	print "Searching for album and genre on wikipedia"
	try:
		print "Trying track name search"
		wiki_search = [x.encode('utf-8') for x in wikipedia.search(track_name + " " + artist, results=5)]
		for i, item in enumerate(wiki_search):
			wiki_page = wikipedia.page(wiki_search[i])
			response = urllib2.urlopen(wiki_page.url).read()
			soup = BeautifulSoup(response, "html.parser")
			if len(soup(text='Genre')) < 1 or len(soup(text='Live album')) > 0:
				continue
			else:
				found = True
				break			
		if not found:
			print "Trying album search"
			wiki_search = [x.encode('utf-8') for x in wikipedia.search(album + " " + artist, results=5)]
			for i, item in enumerate(wiki_search):
				wiki_page = wikipedia.page(wiki_search[i])
				response = urllib2.urlopen(wiki_page.url).read()
				soup = BeautifulSoup(response, "html.parser")
				if len(soup(text='Genre')) < 1:
					continue
				else:
					break
		try:
			album_date = re.search("(\d{4})",soup.find('th', text = re.compile('Released'), attrs={"scope":"row"}).find_next('td').text).group(1)
			print "Album release -", album_date
		except:
			try:
				album_date = re.search("(\d{4})",soup.find('th', text = re.compile('Released'), attrs={"scope":"row"}).find_next('td').text).group(1)
				print "Album release -", album_date
			except:
				print "No album date found"
				album_date = ""
		try:
			genre = soup.find('td', class_="category").text
			genres = filter(None, convert(re.split(',|\n',genre)))
			print "Genre -", genres
			return album_date, genres
		except:
			try:
				genre = soup.find('a', attrs={"title":"Music genre"}).find_next('a').text
				genres = filter(None, convert(re.split(',|\n',genre)))
				print "Genre -", genres
				return album_date, genres
			except:
				print "No genre found"
				genres = ""
				incomplete_meta.append(track_name + '\n')
				with open("incomplete_meta.txt", "a") as myfile:
					myfile.write(track_name + '\n')
				return album_date, genres
	except:
		incomplete_meta.append(track_name + '\n')
		with open("incomplete_meta.txt", "a") as myfile:
			myfile.write(track_name + '\n')
		print "Unable to find article on wikipedia"

		return False

# TODO: Can't get preious element with tag 'bdi'
def get_musicbrainz_data(query): 
	query = urllib.quote(query)
	url = 'https://musicbrainz.org/search?query=' + query + '&type=recording&method=indexed'
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, "html.parser")
	output_to_file(soup.prettify())
	while soup.title.text == 'Search Error':
		response = urllib2.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")
		output_to_file(soup.prettify())
		time.sleep(1)

	print soup.find('td', text = 'Album').text
	print soup.find('td', text = 'Album').find_previous_sibling().text

def fix_tags(file_name, track_data): # [duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres] 0-8
	file_name =  re.sub('[\\\\/:*?"<>|]', '', file_name.rstrip())
	try:
		audio_file = eyed3.load(unidecode.unidecode(file_name + ".mp3"))
		print "Setting id3 tags to", unidecode.unidecode(file_name + ".mp3")
	except:
		try:
			audio_file = eyed3.load(unidecode.unidecode(file_name + ".m4a"))
			print "Setting id3 tags to", unidecode.unidecode(file_name + ".m4a")
		except:
			print "Tagging error"
	try:
		audio_file.tag.title = unicode(track_data[1])
		# audio_file.tag.track_num = unicode(track_data[3])
		audio_file.tag.artist = unicode(track_data[5])
		audio_file.tag.album = unicode(track_data[6])
	except:
		print "Tagging error"
	try:
		audio_file.tag.original_release_date = ''.join(unicode(track_data[7]))
	except Exception as e: 
		# print(e)
		pass
	try:
		audio_file.tag.genre = unicode(re.sub("[^a-zA-Z\s]+", "", track_data[8][0]))
	except:
		pass
	# audio_file.tag.lyrics.set(PyLyrics.getLyrics(track_data[5],track_data[1]))

	# album art
	try:
		response = urllib2.urlopen(track_data[4])  
		image_data = response.read()
		audio_file.tag.images.set(3, image_data , "image/jpeg" ,u"Discription")
		audio_file.tag.save(version=(1,None,None))
		audio_file.tag.save()
		audio_file.tag.save(version=(2,3,0))
	except:
		print "Error fetching album art"
		pass


def main():
	while True:
		print
		print "Enter nothing to exit, ctrl+c to cancel script,"
		print  "\"file\" to enter a file name"
		print
		print "Song Name - Artist"
		text_to_search = raw_input()
		if not text_to_search.strip():
			print incomplete_meta
			sys.exit()
		elif text_to_search.strip() == "file":
			print "File should be in current working directory. Enter file name(txt):"
			file_name = raw_input()
			with open(file_name, 'r') as f:
				num_lines = sum(1 for line in open(file_name))
				count = 1
				for line in f:
					if len(line) > 1:
						print count, "of", num_lines
						count += 1
						try:
							get_da_music(unidecode.unidecode(unicode(line, errors='ignore')))
						except Exception as e:
							print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)
							print "Couldn't get", line
							unable_to_download.append(line + '\n')
							with open("unable_to_download.txt", "a") as myfile:
								myfile.write(line + '\n')
						print
		elif text_to_search.strip() == "spotify":
			get_user_tracks('tylors1', token)
		elif "youtube.com" in text_to_search.strip():
			manual_entry(text_to_search.strip())	
		else:
			get_da_music_no_file(text_to_search)

main()