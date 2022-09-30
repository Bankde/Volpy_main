#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
###### Description ######
# Distributed_sort
###### End of Description ######
'''

import sys, os
import unittest
sys.path.insert(1, os.path.join(sys.path[0], '../utilities'))
import helper

########## Code Here ##########

def partition(collection):        
    # Use the last element as the first pivot
    pivot = collection.pop()
    greater, lesser = [], []
    for element in collection:
        if element > pivot:
            greater.append(element)
        else:
            lesser.append(element)
    return lesser, pivot, greater

def quick_sort_distributed(collection):
    # Tiny tasks are an antipattern. 
    # Thus, in our example we have a "magic number" to 
    # toggle when distributed recursion should be used vs
    # when the sorting should be done in place. The rule
    # of thumb is that the duration of an individual task
    # should be at least 1 second.
    if len(collection) <= 10:  # magic number (Lowered for unittest)
        return sorted(collection)
    else:
        lesser, pivot, greater = partition(collection)
        lesser = quick_sort_distributed(lesser)
        greater = quick_sort_distributed(greater)
        return lesser + [pivot] + greater

import numpy as np

class Test(helper.PickleTest):
    def test_distributed_sort(self):
        self.obj['f1'] = self.dumps(quick_sort_distributed)
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