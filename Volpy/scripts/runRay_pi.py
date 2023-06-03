import ray
import os
import numpy as np
from timeit import default_timer as timer

ray.init()

CORE = int(os.getenv("CORE", 4))
STEP = int(os.getenv("SIZE", 1000 ** 2))

@ray.remote
def pi_monte_carlo():
    circle_points = 0
    square_points = 0
    t1 = timer()
    for i in range(STEP // CORE):
        rand_x = np.random.uniform(-1, 1)
        rand_y = np.random.uniform(-1, 1)
        origin_dist = rand_x**2 + rand_y**2
        if origin_dist <= 1:
            circle_points += 1
        square_points += 1
    t2 = timer()
    return ((t2-t1)*1000, circle_points, square_points)

all_time = []
all_ea_time = []
for j in range(3):
  t1 = timer()
  futures = [pi_monte_carlo.remote() for i in range(CORE)]
  ea_time = []
  circles, squares = 0,0
  for f in futures:
    r = ray.get(f)
    ea_time.append(r[0])
    circles += r[1]
    squares += r[2]
  t2 = timer()
  pi = 4 * circles / squares
  if j == 0: # Debug
    print('PI result: {}'.format(pi))
    print('Time taken: {} ms'.format((t2-t1)*1000))
  all_time.append((t2-t1)*1000)
  all_ea_time.append(ea_time)

import json
with open("result.json", "w") as f:
    json.dump({"total": all_time, "ea": all_ea_time}, f)
print(all_time)
print()
print(all_ea_time)