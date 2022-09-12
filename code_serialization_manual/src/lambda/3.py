src = """
c = 15
x = lambda a, b: a + b + c
"""

exec(src, globals())
assert(x(21, 22) == 58)