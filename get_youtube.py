from bs4 import BeautifulSoup
import youtube_dl
import urllib
import urllib2
import help_us
import re
import unidecode
import os


def get_video_title(download_url):
	soup = BeautifulSoup(urllib2.urlopen(download_url).read(), "html.parser")
	title = soup.title.text[:-10]
	return title

def find_url(track_name, artist):
	count = 0
	# Try to find YouTube's Topic Channel for the track
	search_list = get_search_list(track_name + " " + artist + " topic") # urls, durations, titles, channels
	for item in search_list:
		count += 1
		if "Topic" in item[3] and track_name.lower() in item[2].lower() and "live" not in item[2].lower():
			if count < 2:
				return item[0]
	# No topic channel was found, try other search
	search_list = get_search_list(track_name + " " + artist) # urls, durations, titles, channels
	for item in search_list:
		if "live" not in item[2].lower() and "karaoke" not in item[2].lower():
			return item[0]
	return ""

#URLs from YouTube search
def get_search_list(query):
	print "Searching YouTube for -", query
	query = urllib.quote(query)
	url = "https://www.youtube.com/results?search_query=" + query + "&sp=EgIgAQ%253D%253D"
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, "html.parser")
	vid_list = []
	duration_list = []
	title_list = []
	channel_list = []
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
	    vid_list.append('https://www.youtube.com'.encode('UTF8') + vid['href'].encode('UTF8'))
	# print "Found".encode('UTF8'), len(vid_list), "urls".encode('UTF8')
	for time in soup.findAll(attrs={'class':'video-time'}):
		duration_list.append(help_us.get_sec(time.text.encode('UTF8')))
	for title in soup.findAll(attrs={'aria-describedby':re.compile('description-id')}):
		title_list.append(title.text.encode('UTF8'))
	for channel in soup.findAll(attrs={'class':'yt-lockup-byline '}):
		channel_list.append(channel.text)
	# print "Comparing".encode('UTF8'), len(duration_list), "durations".encode('UTF8')
	search_list = zip(vid_list, duration_list, title_list, channel_list)
	return search_list

# Youtube Download & Convert
def youtube_download(track_name, url, artist):
	print "Downloading and converting..."
	if not artist:
		file_name = str(track_name)
	else:
		file_name = str(artist) + ' - ' + str(track_name)
	print file_name
	file_name = re.sub('[\\\\/:*?"<>|]', '', file_name).rstrip()
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