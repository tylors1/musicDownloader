import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import codecs
import help_us
import get_spotify
import get_wikipedia
import fix_tags
import get_youtube


# client_credentials_manager = SpotifyClientCredentials(client_id='60e52fd7ef4849568a7c057416d33554', client_secret='35bf0fd6643d432c9f0f906c2860f6a3')
username = 'USERNAME'
scope = 'user-library-read'

# Keep track failed meta searches
open('incomplete_meta.txt', 'w').close()
open('unable_to_download.txt', 'w').close()
incomplete_meta = []
unable_to_download = []


def get_da_music(text_to_search, tag_check):
	if "youtube.com" in text_to_search.strip():
		text_to_search, text_to_search_corrected = get_youtube.get_video_title(text_to_search.strip()), ""
	else:
		text_to_search, text_to_search_corrected = help_us.correct_search(text_to_search)
	duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = get_meta_data(text_to_search, text_to_search_corrected)
	if not track_name:
		track_name = text_to_search_corrected if text_to_search_corrected else text_to_search
	if tag_check:
		duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = fix_tags.tag_entry(duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres)
	download_url = get_youtube.find_url(track_name, artist)
	if not all((track_name, cover_art, artist, album, album_date, genres)):
		incomplete_meta.append(text_to_search + '\n')
		with open("incomplete_meta.txt", "a") as myfile:
			myfile.write(text_to_search + '\n')
	if not download_url:
		print "Unable to download"
		unable_to_download.append(track_name + " " + artist + '\n')
		with open("unable_to_download.txt", "a") as myfile:
			myfile.write(track_name + " " + artist + '\n')
		return 0
	file_name = get_youtube.youtube_download(track_name, download_url, artist)
	fix_tags.set_tags(file_name, [duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres])


#Attempts spotify, then wikipedia
def get_meta_data(text_to_search, text_to_search_corrected):
	duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres = (' ',)*9
	duration, track_name, track_id, track_number, cover_art, artist, album = get_spotify.get_spotify_data(text_to_search, text_to_search_corrected)
	if not track_name:
		print "Unable to find meta data from spotify"
	else:
		album_date, genres =  get_wikipedia.get_date_genre(track_name, artist, album)
	return duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres

def main():
	while True:
		print
		print "Enter nothing to exit, ctrl+c to cancel script,"
		print  "\"file\" to enter a file name"
		print
		print "Song Name - Artist or youtube url"
		text_to_search = raw_input()
		if not text_to_search.strip():
			print incomplete_meta
			sys.exit()
		elif text_to_search.strip() == "file":
			print "File should be in current working directory. Enter file name(txt):"
			file_name = raw_input()
			with codecs.open(file_name, 'r') as f:
				num_lines = sum(1 for line in open(file_name))
				for count, line in enumerate(f):
					if len(line) > 1:
						print
						print
						print count, "of", num_lines
						print line
						get_da_music(line, False)
		# elif text_to_search.strip() == "spotify":
			# get_user_tracks('USERNAME')
		else:
			get_da_music(text_to_search, True)

main()