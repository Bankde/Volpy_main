#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

def recursiveFunc(a):
    if a <= 1: return 1
    return a + recursiveFunc(a-1) * recursiveFunc(a-2)

mydump(recursiveFunc)

assert(recursiveFunc(7) == 413747)