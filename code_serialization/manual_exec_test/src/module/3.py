src = """
import numpy.random as rand
from numpy import sum as sum
def sumRandomSeed(a):
    rand.seed(a)
    return sum(rand.randint(0,10,100))
"""

exec(src, globals())
assert(sumRandomSeed(16) == 431)