#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Inherit_class
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname
    def getHeight(self):
        return 180
    def getName(self):
        return "%s %s" % (self.firstname, self.lastname)
class Student(Person):
    def getHeight(self):
        return 160

class Test(helper.PickleTest):
    def test_class_inherit(self):
        self.obj['c1'] = self.dumps(Student)
        o = Student("First", "Last")
        self.assertEqual(o.getName(), "First Last")
        self.assertEqual(o.getHeight(), 160)

    def test_class_inherit_instance(self):
        o = Student("First", "Last")
        self.obj['o1'] = self.dumps(o)
        self.assertEqual(o.getName(), "First Last")
        self.assertEqual(o.getHeight(), 160)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()