#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

class Test(helper.PickleTest):
    def test_func_recursive(self):
        recursive = self.loads(self.obj['f1'])
        self.assertEqual(recursive(5), 15)
        
    def test_func_recursive_double(self):
        recursiveOne = self.loads(self.obj['f1'])
        self.assertEqual(recursiveOne(6), 150)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()