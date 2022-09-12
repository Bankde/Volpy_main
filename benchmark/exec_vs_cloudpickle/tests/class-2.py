#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

print(time("""C = myload()""", globals=globals()))

Computing = myload()
assert(Computing(4,5).compute() == 30)