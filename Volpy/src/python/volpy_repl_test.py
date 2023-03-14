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

async def test_repl():
    print("Test simple task, should return 4")
    def test(i):
        return i+1
    Volpy.registerRemote(test)
    a = test.remote(3)
    print(a.get())
    print("=====================")

    print("Test run 10 times (blocking)")
    for i in range(10):
        print(test.remote(i).get())
    print("=====================")

    print("Test non-blocking longTask")
    import time
    def longTask(i):
        time.sleep(5)
        return i+1
    Volpy.registerRemote(longTask)
    ts = []
    for i in range(10):
        try:
            ts.append(longTask.remote(i))
        except Exception:
            pass
    for t in ts:
        print(t.get())
    print("=====================")

if __name__ == '__main__':
    '''
    Example:
    python volpy_repl.py --rayletipc_addr localhost:50100
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rayletipc_addr", type=str, required=True, help="Specify raylet IPC address")
    args = parser.parse_args()
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ipc_caller.connect(config.rayletipc_addr) # Establish channel with raylet
    loop.run_until_complete(ipc_caller.waitReady())
    volpy_task_manager.TaskManager().setup(ipc_caller)

    loop.run_until_complete(test_repl())
    loop.stop()