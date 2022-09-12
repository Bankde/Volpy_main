# Test shared global (primitive)

g = 300
def funcA():
    global g
    g = g+1
    return g

def funcB():
    global g
    g = g*2
    return g

import codepickle as pickle
p = pickle.dumps([funcA, funcB])
import base64
print(base64.b64encode(p))
f1, f2 = pickle.loads(p)
print(id(f1.__globals__["g"]), id(f2.__globals__["g"]))
print(f1(),f2(),f1(),f1(),f2())
print(id(f1.__globals__["g"]), id(f2.__globals__["g"]))
pass