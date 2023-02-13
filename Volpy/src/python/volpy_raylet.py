import asyncio
import nest_asyncio
nest_asyncio.apply()
import os
import uuid
import subprocess

from lib import raylet_ipc
from lib import raylet_ws as VolpyWS
from lib.config import config

import argparse
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", action="store_true", default=False, help="Set main raylet")
    parser.add_argument("--router", type=str, default="ws://127.0.0.1:8080/ws", help="Specify main raylet router address")
    parser.add_argument("--rayletipc", type=str, default="0", help="Specify raylet ipc binding port")
    parser.add_argument("-w", "--worker", type=int, default=0, help="Specify number of workers to spawn")
    args = parser.parse_args()
    args.uuid = str(os.environ.get("UUID", uuid.uuid4()))
    if not args.main and args.router == "ws://127.0.0.1:8080/ws":
        parser.error("Not a main raylet, need to specify --router to connect to the main raylet.")
    args.rayletipc_addr = f'127.0.0.1:{args.rayletipc}'
    config.merge(args)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run websocket and GRPC
    session, runner = VolpyWS.volpy_ws_create_session_runner(config.uuid, router=config.router, is_main=config.main)
    asyncio.ensure_future(runner.run(session, start_loop=False, log_level='info'), loop=loop)
    ipc_server = raylet_ipc.RayletIPCServer(config.rayletipc_addr)
    config.rayletipc = ipc_server.getRunningPort() # In case port=0
    logging.info(f"Running IPC port: {config.rayletipc}")
    asyncio.ensure_future(ipc_server.run(), loop=loop)
    # Wait for server to complete initialize grpc/websocket before spawning workers
    loop.run_until_complete(asyncio.sleep(1))
    # Spawn workers
    raylet_pid = os.getpid()
    worker_procs = [None]*config.worker
    for i in range(config.worker):
        worker_procs[i] = subprocess.Popen(['python3', 'volpy_worker',
                          '--rayletipc', str(config.rayletipc),
                          '--rayletpid', str(raylet_pid),
                          '--workeripc', str(50100+i)])

    logging.info("Raylet ready")
    loop.run_forever()