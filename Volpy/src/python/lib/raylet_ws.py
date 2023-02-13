from .simple_ws import SimpleWS
from .raylet_scheduler import scheduler as raylet_scheduler, Connection
from .config import config
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.wamp import ApplicationRunner

import asyncio
import json
import logging

class VolpyWS(SimpleWS):
    def addHandler(self):
        # {"task_name": str, "serialized_task": binary}
        # ret: {"status": int}
        self.setCallback("createTask", self.createTask)
        # {"worker_name": str, "cid": int, "task_name": str, "args": binary}
        # ret: {"status": int, "serialized_data": binary}
        # If we receive command to run task from other raylet, 
        # it means main raylet has decided we should run it.
        self.setCallback("workerRun", self.workerRun)
        # {"rayletip": str}
        # ret: {"status": int, "serialized_data": binary}
        self.setCallback("initWorker", self.initWorker)
        # Task Queuing (From other raylet -> main raylet to schedule the task to worker)

    async def createTask(self, task_name, serialized_task):
            """
            Receive CreateTask from ws.
            Raylet has to broadcast the task to all workers (IPC).
            """
            logging.info(f'Recv CreateTask: {task_name}')
            raylet_scheduler.saveTask(task_name, serialized_task)
            workers = raylet_scheduler.getAllLocalWorkers()
            if config.main:
                logging.warn(f'Main raylet receive createTask from WS (ok if you attach REPL to non-main)')
            tasks = []
            # Broadcast to all worker ipc
            for worker in workers:
                task = worker.initTask(task_name, serialized_task=serialized_task)
                tasks.append(task)
            responses = await asyncio.gather(*tasks)
            msg_obj = {"status":0}
            return json.dumps(msg_obj)

    async def workerRun(worker_name, cid, task_name, args):
        logging.info(f'Recv SubmitTask: {cid} {task_name}')
        worker = raylet_scheduler.getWorkerByName(worker_name)
        # There shouldn't be a workerRun call that will redirect us back to ws
        assert(worker.getConnectionType == Connection.IPC)
        response = await worker.runTask(cid, task_name, args) # It's completely fine to await here
        msg_obj = {"status": response.status, "serialized_data": response.serialized_data}
        return json.dumps(msg_obj)

    async def initWorker(self, rayletip):
        # Receive workerInit from ws. Save it and do not redirect it to ws
        worker = raylet_scheduler.addWorker(rayletws=rayletip)
        # No need to distribute task, as it's job for local raylet
        # Logging
        logging.info(f'Worker connect: {worker.worker_name} from rayletip {rayletip}')
        msg_obj = {"status": 0}
        return json.dumps(msg_obj)

def volpy_ws_create_session_runner(uuid, router, realm=None, is_main=False):
    realm = realm if realm else config.realm
    session = VolpyWS(ComponentConfig(realm, {}))
    session.init(uuid, is_main)
    runner = ApplicationRunner(router, realm)
    return session, runner