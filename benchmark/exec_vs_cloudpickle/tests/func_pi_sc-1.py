#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

def findPi():
    # Initialize denominator
    k = 1
    
    # Initialize sum
    s = 0

    for i in range(100000):

        # even index elements are positive
        if i % 2 == 0:
            s += 4/k
        else:

            # odd index elements are negative
            s -= 4/k

        # denominator is odd
        k += 2

    return s

mydump(inspect.getsource(findPi))

assert(findPi() == 3.1415826535897198)