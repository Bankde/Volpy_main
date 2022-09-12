src = """
def pow(a):
    return a*a
def sqSum(a):
    return sum(pow(i) for i in range(1, a+1))
"""

exec(src, globals())
assert(sqSum(4) == 30)