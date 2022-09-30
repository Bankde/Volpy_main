src = """
x = lambda a, b: a + b
"""

exec(src, globals())
assert(x(17, 19) == 36)