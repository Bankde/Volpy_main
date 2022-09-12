src = """
def add_with(c):
    def decorator(function):
        def wrapper(*args, **kwargs):
            ret = function(*args, **kwargs)
            return ret+c
        return wrapper
    return decorator

@add_with(4)
def mymul(a,b,c):
    return a*b*c

@add_with(5)
def mysum(a,b):
    return a + b
"""

exec(src, globals())
assert(mymul(4,5,6) == 124)
assert(mysum(4,5) == 14)