#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

class Test(helper.PickleTest):
    def test_module_simple(self):
        sumRandomSeed = self.loads(self.obj['f1'])
        self.assertEqual(sumRandomSeed(11), 415)
        
    def test_module_alias(self):
        sumRandomSeedAlias = self.loads(self.obj['f1'])
        self.assertEqual(sumRandomSeedAlias(16), 431)

    def test_module_closure(self):
        sumRandomSeed = self.loads(self.obj['f1'])
        self.assertEqual(sumRandomSeed(16), 431)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()