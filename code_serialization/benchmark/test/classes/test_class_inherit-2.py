#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

class Test(helper.PickleTest):
    def test_class_inherit(self):
        Student = self.loads(self.obj['c1'])
        o = Student("First", "Last")
        self.assertEqual(o.getName(), "First Last")
        self.assertEqual(o.getHeight(), 160)

    def test_class_inherit_instance(self):
        o = self.loads(self.obj['o1'])
        self.assertEqual(o.getName(), "First Last")
        self.assertEqual(o.getHeight(), 160)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()