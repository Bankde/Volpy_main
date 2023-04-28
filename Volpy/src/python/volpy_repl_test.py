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

TEST_COUNT = 8
async def test_repl(i):
    match i:
        case 1:
            print("Test distributing task")
            def task1(i):
                return i+1
            def task2(i):
                return i+2
            volpy.registerRemote(task1)
            volpy.registerRemote(task2)
            print("=====================")

        case 2:
            print("Test simple task, should return 4")
            def test(i):
                return i+1
            volpy.registerRemote(test)
            a = test.remote(3)
            print(a.get())
            print("=====================")

        case 3:
            print("Test run 10 times (blocking)")
            def test(i):
                return i+1
            volpy.registerRemote(test)
            for i in range(10):
                print(test.remote(i).get())
            print("=====================")

        case 4:
            print("Test non-blocking longTask")
            import time
            def longTask(i):
                time.sleep(5)
                return i+1
            volpy.registerRemote(longTask)
            ts = []
            for i in range(10):
                try:
                    ts.append(longTask.remote(i))
                except Exception:
                    pass
            for t in ts:
                print(t.get())
            print("=====================")

        case 5:
            print("Test imported module [ret: 7]")
            import numpy as np
            def findMax(i):
                return np.max(i)
            volpy.registerRemote(findMax)
            print(findMax.remote(np.array([1,3,7,2])).get())
            print("=====================")

        case 6:
            print("Test async function [ret: 7]")
            async def callMe(x):
                await asyncio.sleep(2)
                return x
            volpy.registerRemote(callMe)
            print(callMe.remote(7).get())
            print("=====================")

        case 7:
            print("Get and Put from worker [ret: 6]")
            ref1 = volpy.put(5)
            def plusOneToRef(ref):
                d = volpy.get(ref)
                d = d + 1
                ref2 = volpy.put(d)
                return ref2
            volpy.registerRemote(plusOneToRef)
            # Remote -> get return result (ref) -> getValue from ref
            print(plusOneToRef.remote(ref1).get().get())
            print("=====================")

        case 8:
            print("Worker calls remote (req: 2+ workers) [ret: 2]")
            def factorial(i):
                if i > 1:
                    return i * factorial.remote(i-1).get()
                else:
                    return 1
            volpy.registerRemote(factorial)
            print(factorial.remote(2).get())
            print("=====================")

def csv_list(s):
    return [int(x) for x in s.split(",")]

if __name__ == '__main__':
    '''
    Example:
    python volpy_repl.py --rayletipc_addr localhost:50100
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rayletipc_addr", type=str, required=True, help="Specify raylet IPC address")
    parser.add_argument("-i", type=csv_list, default=0, help="Specify testing task (e.g. -i 1 or -i 1,2)")
    args = parser.parse_args()
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ipc_caller.connect(config.rayletipc_addr) # Establish channel with raylet
    loop.run_until_complete(ipc_caller.waitReady())
    volpy_task_manager.TaskManager().setup(ipc_caller)
    volpy.setup(volpy_task_manager)

    if len(config.i) == 1 and config.i[0] == 0:
        config.i = list(range(1,TEST_COUNT+1))
    for i in config.i:
        loop.run_until_complete(test_repl(i))
    loop.stop()
