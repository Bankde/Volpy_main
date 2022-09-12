#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

print(time("""f = myload()""", globals=globals()))

recursiveFunc = myload()
assert(recursiveFunc(7) == 413747)