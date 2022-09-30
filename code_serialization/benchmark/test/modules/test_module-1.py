#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Modules
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

def sumRandomSeed(a):
    import numpy
    numpy.random.seed(a)
    return numpy.sum(numpy.random.randint(0,10,100))

def sumRandomSeedAlias(a):
    import numpy as np
    np.random.seed(a)
    return np.sum(np.random.randint(0,10,100))

def moduleInClosure():
    import numpy as np2
    def sumRandomSeed(a):
        np2.random.seed(a)
        return np2.sum(np2.random.randint(0,10,100))
    return sumRandomSeed

class Test(helper.PickleTest):
    def test_module_simple(self):
        self.obj['f1'] = self.dumps(sumRandomSeed)
        self.assertEqual(sumRandomSeed(11), 415)
        
    def test_module_alias(self):
        self.obj['f1'] = self.dumps(sumRandomSeedAlias)
        self.assertEqual(sumRandomSeedAlias(16), 431)

    def test_module_closure(self):
        sumRandomSeed = moduleInClosure()
        self.obj['f1'] = self.dumps(sumRandomSeed)
        self.assertEqual(sumRandomSeed(16), 431)
        
########## End of Code ##########

if __name__ == "__main__":
    unittest.main()