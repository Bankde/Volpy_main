# closure

def func_add_with(c):
    def my_add(a):
        return a+c
    return my_add

import codepickle
import dis
import inspect

# p = codepickle.dumps(func_add_with)
# c = codepickle.loads(p)
# f = c(5)
# assert(f(7) == 12)
# pass

func = func_add_with(5)
p = codepickle.dumps(func)
f = codepickle.loads(p)
assert(f(7) == 12)
pass