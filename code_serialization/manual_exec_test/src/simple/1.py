src = """
def sum(a, b):
    return a+b
"""

exec(src, globals())
assert(sum(17,18) == 35)