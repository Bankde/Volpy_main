src = """
def sumRandomSeed(a):
    import numpy
    numpy.random.seed(a)
    return numpy.sum(numpy.random.randint(0,10,100))
"""

exec(src, globals())
assert(sumRandomSeed(11) == 415)