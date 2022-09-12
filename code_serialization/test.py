#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import re
from collections import defaultdict
import sys

if len(sys.argv) == 2 and sys.argv[1] in ["srcCode", "src", "srccode", "code", "1"]:
    code = "1"
elif len(sys.argv) == 2 and sys.argv[1] in ["byteCode", "byte", "bytecode", "0"]:
    code = "0"
elif len(sys.argv) == 1:
    code = "1"
else:
    exit("Incorrect input. Allowed: srcCode or byteCode")

# result_file = "result.json" # Same name within the helper.py module
# open(result_file, "w+").close() # Clear the file
test_folder = "src"

testname_re = re.compile("test_(.*).py")

errorTxt = set() # Remove duplicate error

files = os.listdir(test_folder)
path = test_folder
for file in files:
    m = re.match(testname_re, file)
    if m == None: continue
    testset = m.group(1)
    testFileName = file

    try:
        print("-----------------")
        print(testFileName)
        subprocess.check_output(['python', 'src/serialize.py', code, testFileName])
    except Exception as e:
        print(e)
        print("%s: Fail (serialize)" % (testset))
        continue

    try:
        subprocess.check_output(['python', 'src/deserialize.py', code, testFileName])
    except:
        print("%s: Fail (deserialize)" % (testset))
        continue

    print("%s: Pass" % (testset))