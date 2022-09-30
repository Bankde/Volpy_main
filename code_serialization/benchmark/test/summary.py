#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re
import datetime
import json
import pandas as pd
import argparse
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", default="result", help="select data to be summarized")
parser.add_argument('-i', '--inFile', default="result.json", help="write output to file")
parser.add_argument('-o', '--outFile', default="stdout", help="write output to file")
args = parser.parse_args()

result_file = args.inFile # Same name within the helper.py module
if args.outFile == "stdout":
    summary_fh = sys.stdout
else:
    summary_fh = open(args.outFile, "w+")
testname_re = re.compile("test_(\d+)-(\d+).py")

testsuiteNameCache = {}
def getTestsuiteNameFromFile(file):
    global testsuiteNameCache
    s = file.replace("-","/").split("/")
    cur_test = s[-3]+"/"+s[-2]
    with open(file, "r") as f:
        for line in f:
            if line.startswith("###### Description ######"):
                testsuite_name = (f.readline()).strip("#\ \n")
                testsuiteNameCache[cur_test] = testsuite_name
                return testsuite_name

def getTestsuiteName(file):
    global testsuiteNameCache
    s = cur_file.replace("-","/").split("/")
    cur_test = s[-3]+"/"+s[-2]
    return testsuiteNameCache[cur_test]

with open(result_file, "r") as f:
    raw_results = json.load(f)

summary_fh.write("Time: " + raw_results["timestamp"] + "\n")
summary_fh.write("Commit: " + raw_results["commit"] + "\n")

result_dict = {}
for cur_pickle in raw_results["pickleSuites"]:
    result_dict[cur_pickle] = {}
    # First loop to init the dict with testsuite name
    for cur_file in raw_results[cur_pickle]:
        if cur_file.endswith("-1.py"):
            cur_testname = getTestsuiteNameFromFile(cur_file)
            if cur_testname in result_dict[cur_pickle]:
                raise Exception("Impossible flow") # Only one init file should exist.
            result_dict[cur_pickle][cur_testname] = [{} for i in range(2)] # 0/1 for init/test
    # Add the result to our result_dict
    for cur_file in raw_results[cur_pickle]:
        # Get args.data (default: "result") from raw_result
        results = {k: raw_results[cur_pickle][cur_file][k][args.data] if args.data in raw_results[cur_pickle][cur_file][k] else "NA" for k in raw_results[cur_pickle][cur_file]}
        if cur_file.endswith("-1.py"):
            result_dict[cur_pickle][getTestsuiteName(cur_file)][0] = results
        else:
            # There may be several test file
            result_dict[cur_pickle][getTestsuiteName(cur_file)][1].update(results)

# Beauty print with pandas
for testsuite in result_dict[list(result_dict.keys())[0]]:
    df_all_pickles = []
    for cur_pickle in result_dict:
        df = pd.DataFrame(data=result_dict[cur_pickle][testsuite])
        df = df.fillna(' ').T
        df = df.rename(columns={0: "Init(%s)" % (cur_pickle), 1: "Test(%s)" % (cur_pickle)})
        df_all_pickles.append(df)
    result = pd.concat(df_all_pickles, axis=1)
    summary_fh.write("===== Testsuite: %s =====\n" % (testsuite))
    summary_fh.write(str(result))
    summary_fh.write("\n")

if summary_fh is not sys.stdout:
    summary_fh.close()