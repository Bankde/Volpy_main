#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cloudpickle as pickle
import inspect
import timeit
import json
import sys

msg_file = "msg"
result_file = "result.json"

def logToResult(key, value, test_name=None):
    try:
        with open(result_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        data = {}

    if test_name == None:
        test_name = sys.modules['__main__'].__file__.split("/")[-1].split("-")[0]
    if test_name not in data:
        data[test_name] = {}
    data[test_name][key] = value
    with open(result_file, "w+") as f:
        json.dump(data, f)

def mydump(obj):
    with open('msg', 'wb') as f:
        msg = pickle.dumps(obj)
        logToResult("size", len(msg))
        f.write(msg)
        
def myload():
    with open('msg', 'rb') as f:
        return pickle.load(f)
    
def time(run, setup="""""", globals=globals()):
    # Time count for 1000 runs, then repeat 100 times, return array of 100 length
    t = timeit.Timer(run, setup=setup, globals=globals).repeat(100,1000)
    logToResult("time", t)
    return t