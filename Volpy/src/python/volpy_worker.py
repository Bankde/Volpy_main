import asyncio
import nest_asyncio
nest_asyncio.apply()
import os

from lib import worker_executor, worker_ipc, volpy_task_manager
from lib.worker_ipc_caller import ipc_caller
from lib.config import config
import lib.util as util

import argparse
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

async def reaperPoll(pid):
    while True:
        await asyncio.sleep(5)
        if not util.pid_exists(pid):
            os._exit(os.EX_OK)

if __name__ == '__main__':
    '''
    Example:
    python volpy_worker.py --rayletipc 50100 --workeripc 50201
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--rayletipc", type=str, required=True, help="Specify raylet IPC port")
    # default PID 0 will not kill the worker.
    parser.add_argument("--rayletpid", type=int, default=0, help="Specify raylet pid for polling to stop worker")
    parser.add_argument("--workeripc", type=str, default="0", help="Specify worker IPC port")
    args = parser.parse_args()
    args.rayletipc_addr = f'127.0.0.1:{args.rayletipc}'
    args.workeripc_addr = f'127.0.0.1:{args.workeripc}'
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(reaperPoll(config.rayletpid), loop=loop)
    ipc_server = worker_ipc.WorkerIPCServer(config.workeripc_addr)
    config.workeripc = str(ipc_server.getRunningPort()) # In case port=0
    asyncio.ensure_future(ipc_server.run(), loop=loop)

    ipc_caller.connect(config.rayletipc_addr) # Establish channel with raylet
    loop.run_until_complete(ipc_caller.waitReady())
    volpy_task_manager.TaskManager().setup(ipc_caller)
    loop.run_until_complete(ipc_caller.InitWorker(config.workeripc)) # Tell our port to raylet
    response = loop.run_until_complete(ipc_caller.GetAllTasks())
    all_tasks = dict(response.taskmap)
    for task_name in all_tasks:
        worker_executor.initTask(task_name, all_tasks[task_name])
    logging.info("Worker initialized")
    loop.run_forever()