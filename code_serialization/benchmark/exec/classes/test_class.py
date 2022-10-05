#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Classes
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

cls = """
class MyClass():
    def it_work(self):
        return 123
"""

cls2 = """
class AddConstClass():
    def __init__(self, b):
        self.a = 10
        self.b = b
    def sum(self):
        return self.a + self.b

def sumConst(b):
    t = AddConstClass(b)
    return t.sum()
"""

class Test(helper.PickleTest):
    def test_class_simple(self):
        self.exec(cls, globals())
        o = MyClass()
        self.assertEqual(o.it_work(), 123)

    def test_class_object(self):
        self.fail("Not support")
        
    def test_class_nested(self):
        self.exec(cls2, globals())
        self.assertEqual(sumConst(4), 14)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()