src = """
def recursive(a):
    if a == 0: return 0
    return a + recursive(a-1)
"""

exec(src, globals())
assert(recursive(5) == 15)