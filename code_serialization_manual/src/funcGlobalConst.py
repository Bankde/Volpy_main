src = """
c = 10
def sumConst(a):
    return a + c
"""

exec(src, globals())
assert(sumConst(3) == 13)