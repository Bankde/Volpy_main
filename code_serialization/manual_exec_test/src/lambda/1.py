src = """
x = lambda a: a + 10
"""

exec(src, globals())
assert(x(3) == 13)