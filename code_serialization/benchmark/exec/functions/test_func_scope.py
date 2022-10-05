#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Function_scope
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

s1 = """
g = 300
def funcA():
    global g
    g = g+1
    return g
def funcB():
    global g
    g = g*2
    return g
"""

class Test(helper.PickleTest):
    def test_func_shared_scope(self):
        self.exec(s1, globals())
        f1, f2 = funcA, funcB
        self.assertEqual(f1(), 301)
        self.assertEqual(f2(), 602)
        self.assertEqual(f1(), 603)
        self.assertEqual(f1(), 604)
        self.assertEqual(f2(), 1208)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()