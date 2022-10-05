#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Recursive_function
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

recur1 = """
def recursive(a):
    if a == 0: return 0
    return a + recursive(a-1)
"""

recur2 = """
def recursiveTwo(a):
    if a == 0: return 0
    return a + recursiveOne(a-1)
def recursiveOne(a):
    if a == 0: return 0
    return a * recursiveTwo(a-1)
"""

class Test(helper.PickleTest):
    def test_func_recursive(self):
        self.exec(recur1, globals())
        self.assertEqual(recursive(5), 15)
        
    def test_func_recursive_double(self):
        self.exec(recur2, globals())
        self.assertEqual(recursiveOne(6), 150)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()