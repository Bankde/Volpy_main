from multiprocessing import Pool
import numpy as np
import subprocess
from timeit import default_timer as timer
import os

array_size = int(os.getenv("SIZE", 100000000))

def init():
    np.random.seed(13)

def getLastIndex(arr):
    return arr[0]

def test():
    init()

    # Connect the processes in the pool.
    pool = Pool(initializer=init, initargs=(), processes=1)

    # We use int32 here so it's similar to the JS arraybuffer with Int32Array
    arr = np.random.randint(1000000, size=array_size, dtype=np.int32)

    # Time to store object / load
    t1 = timer()
    # Internally pool.map use pickle on the argument so we don't need to do anything here
    s1 = pool.map(getLastIndex, [arr])[0]
    t2 = timer()

    s2 = arr[0]
    assert(s1 == s2)
    print('Time taken {} ms'.format((t2-t1)*1000))

if __name__ == '__main__':
    test()