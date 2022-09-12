#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

def simpleFunc(b):
    a = 123456
    return a*b

mydump(simpleFunc)

assert(simpleFunc(7) == 864192)