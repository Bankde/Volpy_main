from multiprocessing.pool import ThreadPool as Pool
import numpy as np
from timeit import default_timer as timer
import os

CORE = 1
STEP = int(os.getenv("SIZE", 1000 ** 2))

def pi_monte_carlo(i):
    circle_points = 0
    square_points = 0
    for i in range(STEP // CORE):
        rand_x = np.random.uniform(-1, 1)
        rand_y = np.random.uniform(-1, 1)
        origin_dist = rand_x**2 + rand_y**2
        if origin_dist <= 1:
            circle_points += 1
        square_points += 1
    return (circle_points, square_points)

def test():
    # Connect the processes in the pool.
    pool = Pool(processes=CORE)

    # Time to store object / load
    t1 = timer()
    # Internally pool.map use pickle on the argument so we don't need to do anything here
    data = pool.map(pi_monte_carlo, list(range(CORE)))
    t2 = timer()

    circle_points = 0
    square_points = 0
    for d in data:
        circles, squares = d
        circle_points += circles
        square_points += squares
    
    pi = 4 * circle_points / square_points
    # print('PI result: {}'.format(pi))
    # print('Time taken: {} ms'.format((t2-t1)*1000))
    return (t2-t1)*1000

if __name__ == '__main__':
    ts = []
    for i in range(100):
        ts.append(test())
    import json
    with open("result.json", "w") as f:
        json.dump(ts, f)