import os
import sys
import xml.etree.ElementTree as ET

def parse_bible(fn):
  sys.stderr.write("Load %s\n" % fn)
  sys.stderr.flush()
  content = None
  with open(fn) as f:
    content = f.read()
  root = ET.fromstring(content)
  main = None
  for child in root:
    if child.tag == "text":
      main = child[0]
      break

  lang = main.attrib["lang"]
  for book in main:
    chapters = []
    for chapter in book:
      verses = []
      for seg in chapter:
        if seg.text is None: continue
        t = seg.text.strip()
        if lang == "zh":
          t = t.replace(" ", "")
        elif lang == "ko":
          words = t.split("  ")
          t = " ".join([w.replace(" ", "") for w in words])
        verses.append(t)
      chapters.append(" ".join(verses))
    text = "\n".join(chapters)
    yield text

def bible_corpus():
  corpus = []
  for fn in os.listdir("bible"):
    fn = os.path.join("bible", fn)
    for text in parse_bible(fn):
      yield text

def parse_helio(fn):
  print("Load %s" % fn)
  with open(fn) as f:
    for line in f:
      text = line[line.rindex("\t")+1:].strip()
      yield text
    
def helio_corpus():
  for lang in os.listdir("helio"):
    if lang.startswith('.'): continue
    lang_dir = os.path.join("helio", lang)
    for fn in os.listdir(lang_dir):
      if fn.startswith('.'): continue
      fn = os.path.join(lang_dir, fn)
      for text in parse_helio(fn):
        yield text

