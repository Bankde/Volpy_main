src = """
def func_add_with(c):
    def my_add(a):
        return a+c
    return my_add
"""

exec(src, globals())
f = func_add_with(5)
assert(f(9) == 14)
assert(f(10) == 15)