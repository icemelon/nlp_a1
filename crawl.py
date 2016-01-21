import os
import re
import sys
import time
import datetime
import signal
import urllib2
from cookielib import CookieJar
from HTMLParser import HTMLParser

Ignore = 0
Frontpage = 1
Headline = 2

class IndexParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.state = (Ignore, 0)
    self.depth = 0
    self.links = set()
    self.pattern = re.compile("^http://www.nytimes.com/\d")
    
  def handle_starttag(self, tag, attrs):
    #print "Encountered a start tag:", tag
    if tag == "div":
      for key, val in attrs:
        if key == "class" and val == "story":
          self.state = (Frontpage, self.depth)
          break
    elif tag == "ul":
      for key, val in attrs:
        if key == "class" and "headlinesOnly" in val:
          self.state = (Headline, self.depth)
          break
    elif tag == "a":
      if self.state[0] != Ignore:
        for key, val in attrs:
          if key == "href" and re.match(self.pattern, val):
            self.links.add(val)
            break
    self.depth += 1
    
  def handle_endtag(self, tag):
    self.depth -= 1
    if self.state[0] != Ignore and self.state[1] == self.depth:
      self.state = (Ignore, 0)
    
  def handle_data(self, data):
    pass


class ArticleParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.capture = (False, 0)
    self.depth = 0
    self.text = ""

  def handle_starttag(self, tag, attrs):
    if tag == "p":
      for key, val in attrs:
        if key == "class" and "story-body-text" in val:
          self.capture = (True, self.depth)
    self.depth += 1

  def handle_endtag(self, tag):
    self.depth -= 1
    if self.capture[0] and self.capture[1] == self.depth:
      self.capture = (False, 0)
      self.text += "\n"

  def handle_data(self, data):
    if self.capture[0]:
      self.text += data

      
def load_index(date):
  date_str = "%s%s%s" % (date.year, date.month, date.day)
  index_file = os.path.join("data", "index_%s.txt" % date_str)
  if os.path.exists(index_file):
    print("Load index file %s" % index_file)
    links = []
    with open(index_file) as f:
      for line in f:
        links.append(line.strip())
    return links
  index_url = "http://www.nytimes.com/indexes/%s/%02d/%02d/todayspaper/index.html" % (date.year, date.month, date.day)
  print("Fetch index from %s" % index_url)
  # fetch and parse the links
  resp = urllib2.urlopen(index_url)
  html = resp.read()
  parser = IndexParser()
  parser.feed(html)
  
  links = []
  for link in parser.links:
    links.append(link[:link.index("?")])
  with open(index_file, 'w') as f:
    f.write("\n".join(links))
  return links


def fetch_articles(date, links):
  global stop
  date_str = "%s%s%s" % (date.year, date.month, date.day)
  datadir = os.path.join("data", date_str)
  if not os.path.exists(datadir):
    os.mkdir(datadir)
  for link in links:
    if stop: break
    fn = os.path.join(datadir, os.path.basename(link).replace("html", "txt"))
    if not os.path.exists(fn):
      print("Fetch article from %s" % link)
      cj = CookieJar()
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      resp = opener.open(link)
      html = resp.read()
      # extract text
      parser = ArticleParser()
      parser.feed(html)
      with open(fn, 'w') as f:
        f.write(parser.text)

    
def crawl(date):
  print("Crawl ariticles on %s" % date)
  links = load_index(date)
  fetch_articles(date, links)

  
def signal_handler(signal, frame):
  global stop
  stop = True
  print('You pressed Ctrl+C!')


if __name__ == "__main__":
  if not os.path.exists("data"):
    os.mkdir("data")
  global stop
  stop = False
  date = datetime.date.today()
  signal.signal(signal.SIGINT, signal_handler)
  while not stop:
    crawl(date)
    date -= datetime.timedelta(days=1)
    break    

  print("Crawler stopped!")

"""    
today = datetime.date.today()
print(today)
exit()

url = "http://www.nytimes.com/2016/01/21/us/crumbling-destitute-schools-threaten-detroits-recovery.html"
print(url)


#resp = urllib2.urlopen(url)
#html_text = resp.read()
#print(html_text)

parser = IndexParser()
parser.feed(html_text)
print(parser.links)

parser = ArticleParser()
parser.feed(html_text)
print parser.text
"""
