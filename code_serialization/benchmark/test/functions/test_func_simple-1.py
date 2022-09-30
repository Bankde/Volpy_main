#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Functions
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

def sumTwo(a, b):
    return a+b

def sumTwoWithDefault(a, b=5):
    return a+b

def pow(a):
    return a*a
def sqSum(a):
    return sum(pow(i) for i in range(1, a+1))

class Test(helper.PickleTest):
    def test_func_simple(self):
        self.obj['f1'] = self.dumps(sumTwo)
        self.assertEqual(sumTwo(17,18), 35)
        
    def test_func_simple_with_default_arg(self):
        self.obj['f1'] = self.dumps(sumTwoWithDefault)
        self.assertEqual(sumTwoWithDefault(17), 22)
        self.assertEqual(sumTwoWithDefault(17,6), 23)

    def test_func_chain(self):
        self.obj['f1'] = self.dumps(sqSum)
        self.assertEqual(sqSum(4), 30)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()