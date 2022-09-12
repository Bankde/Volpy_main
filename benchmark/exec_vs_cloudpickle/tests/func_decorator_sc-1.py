#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../'))
from helper import mydump, myload, time
import inspect

from functools import wraps

def quote_decorator(function):
    @wraps(function)
    def wrapper(arg1, arg2):
        arg1 = arg1.capitalize()
        arg2 = "\"" + arg2 + "\""
        return function(arg1, arg2)
    return wrapper

@quote_decorator
def sayWithQuote(name, sentence):
    return "{0} says {1}".format(name, sentence)
    
mydump(inspect.getsource(sayWithQuote))

assert(sayWithQuote("john","hello world") == "John says \"hello world\"")