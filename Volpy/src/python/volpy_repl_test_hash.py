import asyncio
import nest_asyncio
nest_asyncio.apply()

from lib import driver_repl, volpy_task_manager
from lib.repl_ipc_caller import ipc_caller
from lib.config import config
import volpy

import argparse
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import numpy as np
from timeit import default_timer as timer

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

async def hashSearchFromWordSubs_dist(s, cur, i, substitute, h, spawn):
    if i >= len(s):
        if hashlib.sha512(cur.encode('utf-8')).hexdigest() == h:
            return cur
        else:
            return None
    proms = []
    for c in substitute[s[i]]:
        if spawn:
            try:
                proms.append(await hashSearchFromWordSubs_dist.remote(s, cur+c, i+1, substitute, h, spawn))
            except:
                spawn = False
                r = await hashSearchFromWordSubs_dist(s, cur+c, i+1, substitute, h, False)
                if r != None:
                    return r
        else:
            r = await hashSearchFromWordSubs_dist(s, cur+c, i+1, substitute, h, False)
            if r != None:
                return r
    for p in proms:
        r = await p.get()
        if r != None:
            return r
    return None

# hash for C0mpu73rEng1n332
h = "79df86177871baa7fa1f0ee88bf1ea9611a473ab441e5f89729961d08586fa98e1d629606712f868f1601516bc0bcd1d66c7886a38a160db1dd77ac12a12ab5e"

async def test_repl(i=0):
    print('Testing v{}'.format(i))
    match i:
        case 1:
            all_time = []
            for j in range(100):
                t1 = timer()
                r = hashSearchFromWordSubs_single("computerengineer", "", 0, subs, h)
                t2 = timer()
                tt = (t2-t1)*1000
                if j == 0: # Debug
                    print(tt, r)
                all_time.append(tt)
            print(all_time)

        case 2:
            all_time = []
            await volpy.registerRemote(hashSearchFromWordSubs_dist)
            for j in range(100):
                t1 = timer()
                p = await hashSearchFromWordSubs_dist.remote("computerengineer", "", 0, subs, h, True)
                r = await p.get()
                t2 = timer()
                tt = (t2-t1)*1000
                if j == 0: # Debug
                    print(tt,r)
                all_time.append(tt)
            print(all_time)

if __name__ == '__main__':
    '''
    Example:
    python volpy_repl.py --rayletipc_addr localhost:50100
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rayletipc_addr", type=str, required=True, help="Specify raylet IPC address")
    parser.add_argument("-i", type=int, default=0, help="Specify testing task (only 1 number)")
    args = parser.parse_args()
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ipc_caller.connect(config.rayletipc_addr) # Establish channel with raylet
    loop.run_until_complete(ipc_caller.waitReady())
    volpy_task_manager.TaskManager().setup(ipc_caller)
    volpy.setup(volpy_task_manager)

    loop.run_until_complete(test_repl(config.i))
    loop.stop()
