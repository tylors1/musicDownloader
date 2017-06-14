import eyed3
from bs4 import BeautifulSoup
import re
import unidecode
import urllib2
import urllib

def tag_entry(duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres):
	print "===== ====="
	print
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
	return duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres

def set_tags(file_name, track_data): # [duration, track_name, track_id, track_number, cover_art, artist, album, album_date, genres] 0-8
	file_name =  re.sub('[\\\\/:*?"<>|]', '', file_name.rstrip())
	try:
		audio_file = eyed3.load(file_name + ".mp3")
		print "Setting id3 tags to", file_name + ".mp3"
	except:
		try:
			audio_file = eyed3.load(file_name + ".m4a")
			print "Setting id3 tags to", file_name + ".m4a"
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

def new_tags(track_name, artist, album, album_date, genres):
	print "Enter nothing to keep found details"
	print "Track name:", track_name
	track_name = enter_details(track_name)
	print "Artist:", artist
	artist = enter_details(artist)
	print "Album:", album
	album = enter_details(album)
	print "Album date:", album_date
	album_date = enter_details(album_date)
	print "Genre:", genres
	genre = enter_details(genres)
	print track_name, artist, album, album_date, genres
	return track_name, artist, album, album_date, genres

def enter_details(variable):
	entry = raw_input()
	if entry.strip():
		return entry
	else:
		return variable		