#!/usr/bin/env python3
import os
import sys
import pickle

from corpus import *

StartSymbol = '\u0002'
StopSymbol = '\u0003'

def train_bigram(model, corpus):
  for text in corpus:
    text = StartSymbol + text + StopSymbol
    for i in range(1, len(text)):
      prev = text[i-1]
      now = text[i-1:i+1]
      if prev not in model: model[prev] = 0
      if now not in model: model[now] = 0
      model[prev] += 1
      model[now] += 1

def train_trigram(model, corpus):
  for text in corpus:
    text = StartSymbol*2 + text + StopSymbol
    for i in range(2, len(text)):
      prev = text[i-2:i]
      now = text[i-2:i+1]
      if prev not in model: model[prev] = 0
      if now not in model: model[now] = 0
      model[prev] += 1
      model[now] += 1

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("%s bi/tri" % sys.argv[0])
    exit()
    
  option = sys.argv[1]
  model_file = None
  model = {}
  
  if option == 'bi':
    model_file = "bigram_model.bin"
    train_bigram(model, bible_corpus())
    train_bigram(model, helio_corpus())
  elif option == 'tri':
    model_file = "trigram_model.bin"
    train_trigram(model, bible_corpus())
    train_trigram(model, helio_corpus())
  else:
    print("Wrong option: %s" % option)
    exit()
    
  binary = pickle.dumps(model)
  with open(model_file, "wb") as f:
    f.write(binary)
  print("Save model to %s" % model_file)
