#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os, sys
from timeit import default_timer as timer
from enum import Enum

if os.getenv("PickleLib"):
    import importlib
    pickle = importlib.import_module(os.getenv("PickleLib"))
else: # Default for testing
    import dill as pickle
if pickle.__name__ == "dill":
    pickle.settings['recurse'] = True

filename = ".data.tmp"
result_file = "result.json"

if "BENCHMARK" in os.environ:
    BENCHMARK = True
    # Total data collected
    BENCHMARK_COUNT = 100
    # Loop for a single execution time
    BENCHMARK_LOOP = 1000
else:
    BENCHMARK = False

def savePickle(obj):
    # Prevent importing whole module as much as possible
    from pickle import dumps
    from base64 import b64encode
    f = open(filename, 'wb+')
    f.write(b64encode(dumps(obj)))
    f.close()

def loadPickle():
    from pickle import loads
    from base64 import b64decode
    f = open(filename, 'rb')
    data = f.readline()
    f.close()
    return loads(b64decode(data))

def saveResult(results):
    import json
    test_name = sys.modules['__main__'].__file__
    # Load prev test
    with open(result_file, "r") as f:
        all_results = json.load(f)
    all_results[pickle.__name__][test_name] = results
    with open(result_file, "w") as f:
        json.dump(all_results, f)

class ResultCode(str, Enum):
    PASS    = "P"
    ERROR   = "E"
    ERR     = "E"
    FAILURE = "F"
    FAIL    = "F"
    MEMORY  = "M"
    MEM     = "M"
    UNKNOWN = "?"
    UNK     = "?"
    CONDITION = "C"
class PickleTest(unittest.TestCase):
    MemSubtestStr = "MemSubtest"

    class TestType(Enum):
        INIT = 1
        TEST = 2

    # Wrapper of pickle dumps and loads
    if BENCHMARK == False:
        def dumps(self, *args, **kwargs):
            try:
                return pickle.dumps(*args, **kwargs)
            except:
                self.pickleError = True
                raise

        def loads(self, *args, **kwargs):
            try:
                return pickle.loads(*args, **kwargs)
            except:
                self.pickleError = True
                raise
    else:
        def dumps(self, *args, **kwargs):
            try:
                time_stat = []
                for i in range(BENCHMARK_COUNT):
                    start = timer()
                    for j in range(BENCHMARK_LOOP):
                        msg = pickle.dumps(*args, **kwargs)
                    stop = timer()
                    time_stat.append(round(stop-start,3))
                # time_stat.sort()
                # avg_stat = sum(time_stat[1:-1])/(len(time_stat)-2) # Remove lowest and highest before avg'ing
                # Unlike original one, we force "one pickle dumps per test" so no double list here.
                self.result[self._testMethodName]["time"] = time_stat
                self.result[self._testMethodName]["size"] = len(msg)
                return msg
            except:
                self.result[self._testMethodName]["time"] = []
                self.result[self._testMethodName]["size"] = -1
                self.pickleError = True
                raise

        def loads(self, *args, **kwargs):
            try:
                time_stat = []
                for i in range(BENCHMARK_COUNT):
                    start = timer()
                    for j in range(BENCHMARK_LOOP):
                        obj = pickle.loads(*args, **kwargs)
                    stop = timer()
                    time_stat.append(round(stop-start,3))
                # time_stat.sort()
                # avg_stat = sum(time_stat[1:-1])/(len(time_stat)-2) # Remove lowest and highest before avg
                self.result[self._testMethodName]["time"] = time_stat
                return obj
            except:
                self.result[self._testMethodName]["time"] = []
                self.pickleError = True
                raise

    def memTest(self, **kwargs):
        return super().subTest(msg=PickleTest.MemSubtestStr)

    '''
    This decorator will force the flag after all of the assertions are passed.
    If one of the assertion is false, the result will still be Failed
    '''
    @staticmethod
    def setFlag(flag, desc):
        def decorator(func):
            func.__test_flag__ = flag
            func.__test_desc__ = desc
            return func
        return decorator

    def generateResultCodeAndMsg(self):
        # https://gist.github.com/hynekcer/1b0a260ef72dae05fe9611904d7b9675
        if hasattr(self, '_outcome'):  # Python 3.4+
            result = self.defaultTestResult()  # these 2 methods have no side effects
            self._feedErrorsToResult(result, self._outcome.errors)
        else:  # Python 3.2 - 3.3 or 2.7
            result = getattr(self, '_outcomeForDoCleanups', self._resultForDoCleanups)
        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)
        mem = self.checkMemSubtest(result.failures)
        '''
        Give result using flags
        E: Error (not picklable)
        F: Failure (Assertion fail)
        M: Mem related (Contained memory address constrain)
        C: Pass with conditions (mostly from setFlag decorator)
        The result can only have 1 flag because the process stops when an error/failure occurs.
        '''
        code = None
        msg = None
        method = getattr(self, self._testMethodName)
        if self.pickleError:
            code = ResultCode.ERROR
            msg = error
        elif error: # Got exception but not from pickle: Need investigation
            code = ResultCode.UNKNOWN
            msg = error
        elif failure:
            code = ResultCode.FAIL
            msg = failure
        elif mem:
            code = ResultCode.MEMORY
            msg = "Pass with memory constrains"
        elif hasattr(method, "__test_flag__"): # Manually set the flag
            code = method.__test_flag__
            msg = method.__test_desc__
        else:
            code = ResultCode.PASS
            msg = ""
        return code, msg

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def checkMemSubtest(self, exc_list):
        if exc_list:
            for fail in exc_list:
                if hasattr(fail[0], "_message") and fail[0]._message == PickleTest.MemSubtestStr:
                    return fail[1]


    def shouldSkipTest(self):
        return self.current_run == self.TestType.TEST and \
            self.main_obj["_result_" + self._testMethodName] != ResultCode.PASS

    '''
    We use this setUp and tearDown pattern so writing testcase can be simple 
    as there is no need to consider duplicated obj key across the different tests
    The process run like this:
        setUpClass -> (setUp -> tearDown)* -> tearDownClass
    '''
    @classmethod
    def setUpClass(cls):
        f = sys.modules['__main__'].__file__
        if f[-5:] == "-1.py":
            cls.current_run = cls.TestType.INIT
            cls.main_obj = {}
        else:
            cls.current_run = cls.TestType.TEST
            cls.main_obj = loadPickle()
        cls.result = {}

    def setUp(self):
        self.result[self._testMethodName] = {}
        # If the previous init fail, we can skip the test
        if self.shouldSkipTest():
            self.result[self._testMethodName]["result"] = ResultCode.ERROR
            self.result[self._testMethodName]["msg"] = "Skip test (init fail)"
            self.skipTest("Skip test (init fail)")
            return
        # Clear previous data
        self.obj = {}
        self.pickleError = False
        # Move respective pickled data from main_obj to obj
        cur_key = "_func_" + self._testMethodName + "_"
        for key in self.main_obj.keys():
            if key.startswith(cur_key):
                new_obj_key = key[len(cur_key):]
                self.obj[new_obj_key] = self.main_obj[key]

    def tearDown(self):
        # Save result for summary
        code, msg = self.generateResultCodeAndMsg()
        self.result[self._testMethodName]["result"] = code
        self.result[self._testMethodName]["msg"] = msg
        # Save pickled data from obj to main_obj
        new_main_obj_key = "_func_" + self._testMethodName + "_"
        for key in self.obj.keys():
            self.main_obj[new_main_obj_key + key] = self.obj[key]
        # Save result into main_obj so we can skip the test if init fail
        result_key = "_result_" + self._testMethodName
        self.main_obj[result_key] = code

    @classmethod
    def tearDownClass(cls):
        if cls.current_run == cls.TestType.INIT:
            savePickle(cls.main_obj)
        # Summary of test result
        saveResult(cls.result)