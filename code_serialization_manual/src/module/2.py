src = """
import numpy as np
def sumRandomSeed(a):
    np.random.seed(a)
    return np.sum(np.random.randint(0,10,100))
"""

exec(src, globals())
assert(sumRandomSeed(16) == 431)