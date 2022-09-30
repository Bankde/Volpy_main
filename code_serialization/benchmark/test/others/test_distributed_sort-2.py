#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

import numpy as np

class Test(helper.PickleTest):
    def test_distributed_sort(self):
        quick_sort_distributed = self.loads(self.obj['f1'])
        np.random.seed(0)
        unsorted = np.random.randint(100, size=(40)).tolist()
        sort = quick_sort_distributed(unsorted)
        ans = [9, 9, 12, 14, 19, 19, 20, 21, 25, 29, 36, 37, 39, 44, \
            46, 47, 47, 49, 58, 64, 64, 65, 67, 67, 69, 70, 72, \
            77, 79, 80, 81, 82, 83, 87, 87, 88, 88, 88, 88, 99]
        self.assertListEqual(sort, ans)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()