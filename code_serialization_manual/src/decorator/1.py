src = """
def add_one(func):
    def inner(*args, **kwargs):
        ret = func(*args, **kwargs)
        return ret+1
    return inner

@add_one
def mymul(a,b,c):
    return a*b*c

@add_one
def mysum(a,b):
    return a + b
"""

exec(src, globals())
assert(mymul(4,5,6) == 121)
assert(mysum(4,5) == 10)