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

func1 = """
def sumTwo(a, b):
    return a+b
"""

func2 = """
def sumTwoWithDefault(a, b=5):
    return a+b
"""

func3 = """
def pow(a):
    return a*a
def sqSum(a):
    return sum(pow(i) for i in range(1, a+1))
"""

class Test(helper.PickleTest):
    def test_func_simple(self):
        self.exec(func1, globals())
        self.assertEqual(sumTwo(17,18), 35)
        
    def test_func_simple_with_default_arg(self):
        self.exec(func2, globals())
        self.assertEqual(sumTwoWithDefault(17), 22)
        self.assertEqual(sumTwoWithDefault(17,6), 23)

    def test_func_chain(self):
        self.exec(func3, globals())
        self.assertEqual(sqSum(4), 30)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()