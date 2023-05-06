import asyncio
import nest_asyncio
nest_asyncio.apply()

from lib import driver_repl, volpy_task_manager
from lib.repl_ipc_caller import ipc_caller
from lib.config import config
import lib.volpy_task_manager as Volpy

import argparse
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

import numpy as np
import time

# MagicSortNumPerCore = (10**6)*3 # Magic number from testing (should be around 0.1s-1s)
MagicSortNumPerCore = (10**4)*3 # Max memory for grpc message
TotalSortNum = MagicSortNumPerCore*2

# Largest grpc: 4194304 bytes
# Largest websocket: 1048576 bytes

def partition(collection):        
    # Use the last element as the first pivot
    pivot = collection.pop()
    greater, lesser = [], []
    for element in collection:
        if element > pivot:
            greater.append(element)
        else:
            lesser.append(element)
    return lesser, pivot, greater

async def quick_sort_distributed(collection):
    # Tiny tasks are an antipattern. 
    # Thus, in our example we have a "magic number" to 
    # toggle when distributed recursion should be used vs
    # when the sorting should be done in place. The rule
    # of thumb is that the duration of an individual task
    # should be at least 1 second.
    if len(collection) <= MagicSortNumPerCore:  # magic number (Lowered for unittest)
        return sorted(collection)
    else:
        lesser, pivot, greater = partition(collection)
        lesser_ref = await quick_sort_distributed.remote(lesser)
        greater_ref = await quick_sort_distributed.remote(greater)
        lesser = await lesser_ref.get()
        greater = await greater_ref.get()
        return lesser + [pivot] + greater

def quick_sort_single_core(collection):
    if len(collection) <= MagicSortNumPerCore:  # magic number (Lowered for unittest)
        return sorted(collection)
    else:
        lesser, pivot, greater = partition(collection)
        lesser = quick_sort_single_core(lesser)
        greater = quick_sort_single_core(greater)
        return lesser + [pivot] + greater

async def test_repl(i=0):
    np.random.seed(0)
    unsorted = np.random.randint(100000, size=(TotalSortNum)).tolist()
    await Volpy.registerRemote(quick_sort_distributed)
    t1 = time.time()
    sort = await (await quick_sort_distributed.remote(unsorted)).get()
    t2 = time.time()
    test_data = [sort[0], sort[10], sort[100], sort[1000], sort[-1]]
    print(f"Time taken (Volpy): {(t2-t1)*1000} ms")

    np.random.seed(0)
    unsorted = np.random.randint(100000, size=(TotalSortNum)).tolist()
    t1 = time.time()
    sort = quick_sort_single_core(unsorted)
    t2 = time.time()
    verf_data = [sort[0], sort[10], sort[100], sort[1000], sort[-1]]
    print(f"Time taken (1 core): {(t2-t1)*1000} ms")

    print("==Verify==")
    print(np.array_equiv(test_data, verf_data))

if __name__ == '__main__':
    '''
    Example:
    python volpy_repl.py --rayletipc_addr localhost:50100
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rayletipc_addr", type=str, required=True, help="Specify raylet IPC address")
    parser.add_argument("-i", type=int, default=0, help="Specify testing task")
    args = parser.parse_args()
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ipc_caller.connect(config.rayletipc_addr) # Establish channel with raylet
    loop.run_until_complete(ipc_caller.waitReady())
    volpy_task_manager.TaskManager().setup(ipc_caller)

    loop.run_until_complete(test_repl(config.i))
    loop.stop()
