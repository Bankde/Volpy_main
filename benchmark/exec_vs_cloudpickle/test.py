#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import re
import helper
from collections import defaultdict

result_file = "result.json" # Same name within the helper.py module
open(result_file, "w+").close() # Clear the file
test_folder = "tests"

testname_re = re.compile("(\w+)-(\d+).py")

errorTxt = set() # Remove duplicate error

files = os.listdir(test_folder)
testsets = defaultdict(lambda: 0)
path = test_folder
for file in files:
    match = re.match(testname_re, file)
    if match == None:
        continue
    testsets[match.group(1)] += 1

for testset in sorted(testsets.keys()):
    if testsets[testset] < 2:
        errorTxt.add("Error incomplete testset: %s %s" % (testset))
        continue

    testsetName = os.path.join(path, testset)
    # Note: the "-1.py" will always be init'ed test.
    for i in range(1,3):
        try:
            testPickle = testsetName + "-%d.py" % (i)
            subprocess.check_output(['python', testPickle])
        except:
            helper.logToResult("error", "Exception raised.", test_name=testset)

if len(errorTxt) > 0:
    print("Testsuite with error:")
    print(errorTxt)