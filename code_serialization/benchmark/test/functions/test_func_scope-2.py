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

class Test(helper.PickleTest):
    def test_func_shared_scope(self):
        f1, f2 = self.loads(self.obj['b1'])
        self.assertEqual(f1(), 301)
        self.assertEqual(f2(), 602)
        self.assertEqual(f1(), 603)
        self.assertEqual(f1(), 604)
        self.assertEqual(f2(), 1208)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()