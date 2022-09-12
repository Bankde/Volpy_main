#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

class Computing():
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def _computeA(self):
        s = 0
        for i in range(self.a):
            s += i
        return s
            
    def _computeB(self):
        s = 1
        for i in range(1, self.b):
            s *= i
        return s
        
    def compute(self):
        return self._computeA() + self._computeB()
    
mydump(inspect.getsource(Computing))

assert(Computing(4,5).compute() == 30)