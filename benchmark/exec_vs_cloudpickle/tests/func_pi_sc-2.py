#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

print(time("""exec(myload(), globals())""", globals=globals()))

exec(myload(), globals())
assert(findPi() == 3.1415826535897198)