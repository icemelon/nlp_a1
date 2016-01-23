#!/usr/bin/env python3

import os
import sys
import math
import pickle
import random
import codecs

StartSymbol = '\u0002'
StopSymbol = '\u0003'
SymbolSize = 65392

def load_model(fn):
  binary = None
  with open(fn, "rb") as f:
    binary = f.read()
  return pickle.loads(binary, encoding="utf-8")

class Bigram:
  def __init__(self, model, iota=1e-4):
    self.iota = iota
    self.model = model
    self.history = StartSymbol

  def add(self, c):
    if c == StopSymbol:
      print("// added Stop symbol, clear the history!")
      self.history = StartSymbol
    else:
      print("// added a character to the history!")
      self.history += c

  def query(self, c):
    prev = self.history[-1]
    pair = prev + c
    c_pair = 0
    c_prev = 0
    if pair in self.model: c_pair = self.model[pair]
    if prev in self.model: c_prev = self.model[prev]
    prob = (c_pair + self.iota) / (c_prev + SymbolSize * self.iota)
    log_prob = math.log(prob, 2)
    print(log_prob)

  def generate(self):
    symbol_dist = {}
    pool = []
    
    prev = self.history[-1]
    c_prev = 0
    if prev in self.model: c_prev = self.model[prev]
    
    for i in range(0x10000):
      # skip unallocated blocks
      if (i >= 0x0860 and i <= 0x089F) or (i >= 0x1C80 and i <= 0x1CBF) or \
         (i >= 0x2FE0 and i <= 0x2FEF):
        continue
      c = chr(i)
      pair = prev + c
      c_pair = 0
      if pair in self.model: c_pair = self.model[pair]
      prob = (c_pair + self.iota) / (c_prev + SymbolSize * self.iota)
      symbol_dist[c] = prob
      for _ in range(round(prob * 65536)):
        pool.append(c)

    ch = random.choice(pool)
    log_prob = math.log(symbol_dist[ch], 2)
    print("%s // generated a character! prob of generation: %s" % (ch, log_prob))
    if ch == StopSymbol:
      self.history = StartSymbol
    else:
      self.history += ch


class Trigram:
  def __init__(self, model, iota=1e-4):
    self.iota = iota
    self.model = model
    self.history = StartSymbol * 2

  def add(self, c):
    if c == StopSymbol:
      print("// added Stop symbol, clear the history!")
      self.history = StartSymbol * 2
    else:
      print("// added a character to the history!")
      self.history += c

  def query(self, c):
    prev = self.history[-1]
    pair = prev + c
    c_pair = 0
    c_prev = 0
    if pair in self.model: c_pair = self.model[pair]
    if prev in self.model: c_prev = self.model[prev]
    prob = (c_pair + self.iota) / (c_prev + SymbolSize * self.iota)
    log_prob = math.log(prob, 2)
    print(log_prob)

  def generate(self):
    symbol_dist = {}
    pool = []
    
    prev = self.history[-1]
    c_prev = 0
    if prev in self.model: c_prev = self.model[prev]
    
    for i in range(0x10000):
      # skip unallocated blocks
      if (i >= 0x0860 and i <= 0x089F) or (i >= 0x1C80 and i <= 0x1CBF) or \
         (i >= 0x2FE0 and i <= 0x2FEF):
        continue
      c = chr(i)
      pair = prev + c
      c_pair = 0
      if pair in self.model: c_pair = self.model[pair]
      prob = (c_pair + self.iota) / (c_prev + SymbolSize * self.iota)
      symbol_dist[c] = prob
      for _ in range(round(prob * 65536)):
        pool.append(c)

    ch = random.choice(pool)
    log_prob = math.log(symbol_dist[ch], 2)
    print("%s // generated a character! prob of generation: %s" % (ch, log_prob))
    if ch == StopSymbol:
      self.history = StartSymbol
    else:
      self.history += ch


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("%s random_seed" % (sys.argv[0]))
    exit()
  seed = int(sys.argv[1])
  random.seed(seed)
  model = load_model("model.bin")

  worker = Bigram(model)
  while True:
    c = sys.stdin.read(1)
    if c == 'o':
      c = sys.stdin.read(1)
      worker.add(c)
    elif c == 'q':
      c = sys.stdin.read(1)
      worker.query(c)
    elif c == 'g':
      worker.generate()
    elif c == 'x':
      break
