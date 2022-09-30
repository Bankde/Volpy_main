#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Closure
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

def func_add_with(c):
    def my_add(a):
        return a+c
    return my_add

class Test(helper.PickleTest):
    def test_func_closure(self):
        f1 = func_add_with(4)
        self.obj['f1'] = self.dumps(f1)
        self.assertEqual(f1(11), 15)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()