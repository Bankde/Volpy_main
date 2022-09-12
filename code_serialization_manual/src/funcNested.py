src = """
def sqSum(a):
    def pow(b):
        return b*b
    return sum(pow(i) for i in range(1, a+1))
"""

exec(src, globals())
assert(sqSum(4) == 30)