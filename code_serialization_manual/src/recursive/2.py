src = """
def recursiveTwo(a):
    if a == 0: return 0
    return a + recursiveOne(a-1)
def recursiveOne(a):
    if a == 0: return 0
    return a * recursiveTwo(a-1)
"""

exec(src, globals())
assert(recursiveOne(6) == 150)