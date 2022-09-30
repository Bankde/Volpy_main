#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########
class Test(helper.PickleTest):
    def test_func_simple(self):
        sumTwo = self.loads(self.obj['f1'])
        self.assertEqual(sumTwo(17,18), 35)
        
    def test_func_simple_with_default_arg(self):
        sumTwoWithDefault = self.loads(self.obj['f1'])
        self.assertEqual(sumTwoWithDefault(17), 22)
        self.assertEqual(sumTwoWithDefault(17,6), 23)

    def test_func_chain(self):
        sqSum = self.loads(self.obj['f1'])
        self.assertEqual(sqSum(4), 30)

########## End of Code ##########

if __name__ == "__main__":
    unittest.main()