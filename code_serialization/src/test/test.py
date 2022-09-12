# Test globals with same name on different scopes

t1 = None
t2 = None
def funcA():
    global t1
    g = 10
    def test():
        return g
    t1 = test
funcA()

def funcB():
    global t2
    g = 3
    def test():
        return t1()*g
    t2 = test
funcB()

import cloudpickle
cloudpickle.dumps(funcB)