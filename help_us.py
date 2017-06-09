import collections
import urllib
from bs4 import BeautifulSoup
import urllib2
import sys

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
		text_file.write(data)
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

# piggyback youtube's spellchecker & query corrector
def correct_search(text_to_search): 
    url = "https://www.youtube.com/results?search_query=" + urllib.quote(text_to_search) + "&sp=EgIgAQ%253D%253D"
    soup = BeautifulSoup(urllib2.urlopen(url).read(), "html.parser")
    text_to_search_corrected = ""
    output_to_file(soup.encode('UTF-8'))
    try:
        text_to_search_corrected = soup.find('span', attrs={"class":"spell-correction-corrected"}).find_next('a').getText()
        print "Searching instead for -", text_to_search_corrected
    except Exception as e: # Exception expected when no spell correction is found
        # print(e)
        print "Searching for -", text_to_search
    return text_to_search, text_to_search_corrected
