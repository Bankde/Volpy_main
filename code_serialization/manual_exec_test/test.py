#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import subprocess
import re
from collections import defaultdict
import sys

pad = 2
test_folder = os.path.abspath("src")

testname_re = re.compile("test_(.*).py")

errorTxt = set() # Remove duplicate error

def runTestInFolder(folder, indent=0):
    files = os.listdir(folder)
    files.sort()
    for file in files:
        abs_file = os.path.join(folder, file)
        if os.path.isdir(abs_file):
            print(' '*pad*indent + file + ":")
            runTestInFolder(abs_file, indent=indent+1)
            continue
    
        try:
            subprocess.check_output(['python', abs_file])
        except Exception as e:
            # print(e)
            print(' '*pad*indent + "%s: Fail (serialize)" % (file))
            continue

        print(' '*pad*indent + "%s: Pass" % (file))

runTestInFolder(test_folder)