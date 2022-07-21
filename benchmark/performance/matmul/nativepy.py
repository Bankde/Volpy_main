import numpy as np
from numpy.testing import assert_array_equal
from timeit import default_timer as timer
import os

if "SIZE" in os.environ:
    size = int(os.environ["SIZE"])
else:
    size = 125

def matmul(A, B, C):
    # Assume 2 identical-size NxN matrix
    N = A.shape[0]
    for i in range(N):
        for j in range(N):
            sum = 0
            for k in range(N):
                sum += A[i][k] * B[k][j]
            C[i][j] = sum

def genMat(size):
    # [-10,10]
    return np.random.randint(-10, 11, size=(size, size))

def test():
    A = genMat(5)
    B = genMat(5)
    C = np.zeros((5,5))
    matmul(A,B,C)
    assert_array_equal(C, np.matmul(A,B))

test()
print("Testing size: %d" % size)
A = genMat(size)
B = genMat(size)
C = np.zeros((size,size))
start = timer()
matmul(A, B, C)
end = timer()
t = (end - start)*1000
print("Time: %.1f" % t)


