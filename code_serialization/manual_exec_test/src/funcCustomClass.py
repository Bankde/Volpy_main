src = """
class Test():
    def __init__(self, b):
        self.a = 10
        self.b = b
    def sum(self):
        return self.a + self.b

def sumConst(b):
    t = Test(b)
    return t.sum()
"""

exec(src, globals())
assert(sumConst(4) == 14)