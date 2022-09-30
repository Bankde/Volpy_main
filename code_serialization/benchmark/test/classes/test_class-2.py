#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

class Test(helper.PickleTest):
    def test_class_simple(self):
        MyClass = self.loads(self.obj['c1'])
        o = MyClass()
        self.assertEqual(o.it_work(), 123)

    def test_class_object(self):
        o = self.loads(self.obj['o1'])
        self.assertEqual(o.it_work(), 123)
        
    def test_class_nested(self):
        sumConst = self.loads(self.obj['f1'])
        self.assertEqual(sumConst(4), 14)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()