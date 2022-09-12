# Test simple function

def funcA(a, b):
    return a+b

import codepickle
p = codepickle.dumps(funcA)
f1 = codepickle.loads(p)
print(p)
print(f1)
print(f1(4,9))
assert(f1(4,9) == 13)