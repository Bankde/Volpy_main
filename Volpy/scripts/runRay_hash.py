import numpy as np
from timeit import default_timer as timer
import ray
import asyncio

'''
This test is NOT used. Ray spawned new task infinitely so it's ineffective to use the same code.
'''
ray.init()

import string
subs = {}
for c in string.ascii_lowercase:
    subs[c] = [c.lower(), c.upper()]
def addSubs(char, sub):
    global subs
    subs[char] += sub
addSubs("a", ["4","@"])
addSubs("b", ["8"])
addSubs("e", ["3"])
addSubs("g", ["6"])
addSubs("i", ["l","1","!"])
addSubs("l", ["i","1","!"])
addSubs("o", ["0"])
addSubs("r", ["2"])
addSubs("s", ["5","$"])
addSubs("t", ["7"])
addSubs("z", ["2"])

import hashlib
def hashSearchFromWordSubs_single(s, cur, i, substitute, h):
    if i >= len(s):
        if hashlib.sha512(cur.encode('utf-8')).hexdigest() == h:
            return cur
        else:
            return None
    for c in substitute[s[i]]:
        r = hashSearchFromWordSubs_single(s, cur+c, i+1, substitute, h)
        if r != None:
            return r
    return None

@ray.remote
def hashSearchFromWordSubs_dist(s, cur, i, substitute, h, spawn):
    if i >= len(s):
        if hashlib.sha512(cur.encode('utf-8')).hexdigest() == h:
            return cur
        else:
            return None
    pending = set() # Storing runTask
    for c in substitute[s[i]]:
        if spawn:
            try:
                t = hashSearchFromWordSubs_dist.remote(s, cur+c, i+1, substitute, h, spawn)
                pending.add(t)
            except:
                spawn = False
                r = hashSearchFromWordSubs_single(s, cur+c, i+1, substitute, h)
                if r != None:
                    return r
        else:
            r = hashSearchFromWordSubs_single(s, cur+c, i+1, substitute, h)
            if r != None:
                return r
    # We want to get result from Volpy.get()
    # Ray doesn't fully support asyncio yet
    for ref in pending:
        r = ray.get(ref)
        if r != None:
            return r
    return None

# hash for C0mpu73rEng1n332
h = "79df86177871baa7fa1f0ee88bf1ea9611a473ab441e5f89729961d08586fa98e1d629606712f868f1601516bc0bcd1d66c7886a38a160db1dd77ac12a12ab5e"

all_time = []
for j in range(3):
  t1 = timer()
  ref = hashSearchFromWordSubs_dist.remote("computerengineer", "", 0, subs, h, True)
  result = ray.get(ref)
  t2 = timer()
  tt = (t2-t1)*1000
  if j == 0: # Debug
      print(tt,result)
  all_time.append(tt)
  print(all_time)