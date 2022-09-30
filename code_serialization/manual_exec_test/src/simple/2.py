src = """
def sum(a, b=5):
    return a+b
"""

exec(src, globals())
assert(sum(17) == 22)
assert(sum(18, 9) == 27)