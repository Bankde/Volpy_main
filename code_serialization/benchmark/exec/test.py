#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import re
from collections import defaultdict
import datetime
import json
import pandas as pd

result_file = "result.json" # Same name within the helper.py module

testSuites = [
    "functions",
    "modules",
    "classes",
    "others"
]
pickleSuites = [
    "exec"
]

testname_re = re.compile("test_(\w+).py")

# https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
def get_git_revision_hash() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except:
        return "None"

def initResultFile():
    all_results = {}
    for p in pickleSuites:
        all_results[p] = {}
    all_results["timestamp"] = str(datetime.datetime.now())
    all_results["commit"] = get_git_revision_hash()
    all_results["pickleSuites"] = pickleSuites
    with open(result_file, "w+") as f:
        json.dump(all_results, f)

initResultFile()

errorTxt = set() # Remove duplicate error

for pickle in pickleSuites:
    new_env = os.environ
    new_env["PickleLib"] = pickle
    print("===== Testing for %s =====" % (pickle))
    for testSuite in testSuites:
        path = os.path.join(sys.path[0], testSuite)
        files = os.listdir(path)
        testsets = defaultdict(lambda: 0)
        for file in files:
            match = re.match(testname_re, file)
            if match == None:
                continue

            testset = match.group(1)
            testsetName = os.path.join(path, "test_" + testset)
            try:
                testPickle = testsetName + ".py"
                subprocess.check_output(['python', testPickle], env=new_env)
            except:
                # We ignore the exceptions raised from the tests
                pass

if len(errorTxt) > 0:
    print("Testsuite with error:")
    print(errorTxt)