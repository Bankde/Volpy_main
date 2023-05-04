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

async def test_repl():
    print("Init test init task")
    def task1(i):
        return i+1
    def task2(i):
        return i+2
    await volpy.registerRemote(task1)
    await volpy.registerRemote(task2)
    print("=====================")

    print("Init test run task")
    def test(i):
        return i+1
    await volpy.registerRemote(test)
    a = await test.remote(3)
    print(await a.get())
    print("=====================")

    print("Init test dataref")
    data = 13.45
    dataref = await volpy.put(data)
    print(dataref)
    print("=====================")

    input("Go launch another raylet and press Enter to continue...")

    print("Test init task (Res: 4)")
    print(await (await task1.remote(3)).get())
    print("=====================")

    print("Test run task (Res: [3-7])")
    def test2(i):
        return i+3
    await volpy.registerRemote(test2)
    for i in range(5):
        a = await test2.remote(i)
        print(await a.get())
    print("=====================")

    print("Test dataref (Res: 13.45)")
    print(await volpy.get(dataref))
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
    volpy.setup(volpy_task_manager)

    loop.run_until_complete(test_repl())
    loop.stop()
