import urllib
from bs4 import BeautifulSoup
import urllib2
import sys
import wikipedia
import re

def get_date_genre(track_name, artist):
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
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)
			try:
				album_date = re.search("(\d{4})",soup.find('th', text = re.compile('Released'), attrs={"scope":"row"}).find_next('td').text).group(1)
				print "Album release -", album_date
			except:
				print "No album date found"
				album_date = ""
		try:
			genre = soup.find('td', class_="category").text
			genres = filter(None, (re.split(',|\n',genre)))
			print "Genre -", genres
			return album_date, genres
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)
			try:
				genre = soup.find('a', attrs={"title":"Music genre"}).find_next('a').text
				genres = filter(None, re.split(',|\n',genre))
				print "Genre -", genres
				return album_date, genres
			except:
				print "No genre found"
				genres = ""
				return album_date, genres
	except Exception as e:
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)

		return "",""