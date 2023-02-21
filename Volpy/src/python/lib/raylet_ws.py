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
        # {"cid": int, "task_name": str, "args": binary}
        # ret: {"status": int, "serialized_data": binary} 
        # Send the runTask req to the main raylet schedule to decide which worker should run it.
        # This command should only be called from other raylet to main.
        self.setCallback("reqRunTask", self.reqRunTask)
        # {"worker_name": str, "cid": int, "task_name": str, "args": binary}
        # ret: {"status": int, "serialized_data": binary}
        # An order command from main raylet that we should run the task on this node.
        # This should NOT be called directly from the user, should call reqRunTask instead.
        self.setCallback("workerRun", self.workerRun)
        # {"rayletip": str}
        # ret: {"status": int, "serialized_data": binary}
        # Tell the main raylet that new worker has been connected.
        # The scheduler will save 
        self.setCallback("initWorker", self.initWorker)

    async def createTask(self, data):
            """
            Receive CreateTask from raylet (either main/not) ws.
            Raylet has to broadcast the task to all workers (IPC).
            """
            task_name, serialized_task = data["task_name"], data["serialized_task"]
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

    async def reqRunTask(self, data):
        cid, task_name, args = data["cid"], data["task_name"], data["args"]
        logging.info(f'Recv reqRunTask: {cid} {task_name}')

    async def workerRun(self, data):
        worker_name, cid, task_name, args = data["worker_name"], data["cid"], data["task_name"], data["args"]
        logging.info(f'Recv SubmitTask: {cid} {task_name}')
        worker = raylet_scheduler.getWorkerByName(worker_name)
        # There shouldn't be a workerRun call that will redirect us back to ws
        assert(worker.getConnectionType == Connection.IPC)
        response = await worker.runTask(cid, task_name, args) # It's completely fine to await here
        msg_obj = {"status": response.status, "serialized_data": response.serialized_data}
        return json.dumps(msg_obj)

    async def initWorker(self, data):
        rayletip = data["rayletip"]
        # Receive workerInit from ws. Save it and do not redirect it to ws
        worker = raylet_scheduler.addWorker(rayletws=rayletip)
        # No need to distribute task, as local raylet will do it in ipc.
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