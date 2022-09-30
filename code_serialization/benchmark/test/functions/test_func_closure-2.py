#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

class Test(helper.PickleTest):
    def test_func_closure(self):
        f1 = self.loads(self.obj['f1'])
        self.assertEqual(f1(11), 15)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()