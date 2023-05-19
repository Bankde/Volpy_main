import asyncio
import nest_asyncio
nest_asyncio.apply()

from lib import driver_repl, volpy_task_manager
from lib.repl_ipc_caller import ipc_caller
from lib.config import config
import volpy

import argparse
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import numpy as np
from timeit import default_timer as timer
import os

CORE = int(os.getenv("CORE", 4))
STEP = int(os.getenv("SIZE", 1000 ** 2))

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

async def test_repl(i=0):
    print('Testing size: {} on {} cores, v{}'.format(STEP, CORE, i))
    match i:
        case 1:
            all_time = []
            for j in range(100):
                t, cp, sp = pi_monte_carlo()
                pi = 4 * cp / sp
                all_time.append(t)
                if j == 0:
                    print('PI result: {}'.format(pi))
                    print('Time taken: {} ms'.format(t))
            import json
            with open("result.json", "w") as f:
                json.dump({"total": all_time}, f)
            print(all_time)

        case 2:
            all_time = []
            all_ea_time = []
            await volpy.registerRemote(pi_monte_carlo)
            for j in range(100):
                ts = []
                ea_time = []
                t1 = timer()
                for k in range(CORE):
                    t = await pi_monte_carlo.remote()
                    ts.append(t)
                circles, squares = 0,0
                for t in ts:
                    pts = await t.get()
                    ea_time.append(pts[0])
                    circles += pts[1]
                    squares += pts[2]
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

if __name__ == '__main__':
    '''
    Example:
    python volpy_repl.py --rayletipc_addr localhost:50100
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rayletipc_addr", type=str, required=True, help="Specify raylet IPC address")
    parser.add_argument("-i", type=int, default=0, help="Specify testing task (only 1 number)")
    args = parser.parse_args()
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ipc_caller.connect(config.rayletipc_addr) # Establish channel with raylet
    loop.run_until_complete(ipc_caller.waitReady())
    volpy_task_manager.TaskManager().setup(ipc_caller)
    volpy.setup(volpy_task_manager)

    loop.run_until_complete(test_repl(config.i))
    loop.stop()
