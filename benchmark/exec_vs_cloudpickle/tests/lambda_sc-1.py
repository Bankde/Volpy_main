#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

f = lambda a : a + 10

mydump(inspect.getsource(f))

assert(f(7) == 17)