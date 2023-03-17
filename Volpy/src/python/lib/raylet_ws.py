from .simple_ws import SimpleWS
from .config import config
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.wamp import ApplicationRunner
from .raylet_scheduler import scheduler, datastore, Connection, fire_and_forget_task

from .util import Status, generateDataRef

import asyncio
import json
import logging
from enum import IntEnum

# Singleton
session = None

class VolpyWS(SimpleWS):
    class API(IntEnum):
        Nop = 0
        CreateTask = 1
        GetAllTasks = 2

        InitWorker = 11
        AcquireWorker = 12
        FreeWorker = 13
        WorkerRun = 14

        SaveDataRef = 21
        GetData = 22

    def addHandler(self):
        # {"task_name": str, "serialized_task": bytes}
        # ret: {"status": int}
        self.setCallback(self.API.CreateTask, self.createTask)
        # {}
        # ret: {"taskmap": dict<name, bytes>}
        self.setCallback(self.API.GetAllTasks, self.getAllTasks)
        # {"cid": int, "task_name": str, "args": bytes}
        # ret: {"status": int, "worker_id": str} 
        # Acquire worker from main raylet. Lock the worker.
        self.setCallback(self.API.AcquireWorker, self.acquireWorker)
        # {"cid": int, "worker_id": str"}
        # ret: {"status": int}
        # Unlock the worker.
        self.setCallback(self.API.FreeWorker, self.freeWorker)
        # {"cid": int, "worker_id": str, "task_name": str, "args": bytes}
        # ret: {"status": int, "dataref": str}
        # A command to run the task on this node. Behave like running task with ipc.
        # Will broadcast dataref to other nodes with its rayletid.
        # Return dataref, the result data of the task will store locally.
        self.setCallback(self.API.WorkerRun, self.workerRun)
        # {"rayletid": str}
        # ret: {"status": int, "worker_id": str}
        # Tell the main raylet that new worker has been connected.
        # The scheduler will save worker in the list and return the new assigned Id
        self.setCallback(self.API.InitWorker, self.initWorker)
        # {"dataref": str, "rayletid": str}
        # ret: {"status": int}
        # Tell raylet that the pair of dataRef and its location
        self.setCallback(self.API.SaveDataRef, self.saveDataRef)
        # {"dataref": str}
        # ret: {"status": int, "serialized_data": bytes}
        # Get data from ref
        self.setCallback(self.API.GetData, self.getData)

    async def createTask(self, data):
        """
        Receive CreateTask from raylet (either main/not) ws.
        Raylet has to broadcast the task to all workers (IPC).
        """
        task_name, serialized_task = data["task_name"], data["serialized_task"]
        logging.info(f'Recv CreateTask: {task_name}')
        scheduler.saveTask(task_name, serialized_task)
        workers = scheduler.getAllLocalWorkers()
        if config.main:
            logging.warn(f'Main raylet receive createTask from WS (ok if you attach REPL to non-main)')
        tasks = []
        # Broadcast to all worker ipc
        for worker in workers:
            task = worker.initTask(task_name, serialized_task=serialized_task)
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        msg_obj = {"status": Status.SUCCESS}
        return msg_obj
    
    async def getAllTasks(self, data):
        """
        Return all of the declared tasks
        """
        data = scheduler.getAllTasks()
        msg_obj = {"taskmap": data}
        return msg_obj

    async def acquireWorker(self, data):
        cid, task_name, args = data["cid"], data["task_name"], data["args"]
        logging.info(f'Recv AcquireWorker: {cid} {task_name}')
        worker = scheduler.acquireWorker()
        if worker == None:
            logging.info(f'All worker busy: {cid}')
            msg_obj = {"status": Status.WORKER_BUSY, "worker_id": "-1"}
            return msg_obj
        logging.info(f'Worker acquire: {cid} {worker.getId()}')
        msg_obj = {"status": Status.SUCCESS, "worker_id": worker.getId()}
        return msg_obj
    
    async def freeWorker(self, data):
        cid, worker_id = data["cid"], data["worker_id"]
        logging.info(f'Recv FreeWorker: {cid} {worker_id}')
        scheduler.getWorkerById(worker_id).unlock()
        msg_obj = {"status": Status.SUCCESS, "worker_id": worker_id}
        return msg_obj

    async def workerRun(self, data):
        cid, worker_id, task_name, args = data["cid"], data["worker_id"], data["task_name"], data["args"]
        logging.info(f'Recv workerRun: {cid} {worker_id} {task_name}')
        worker = scheduler.getWorkerById(worker_id)
        # There shouldn't be a workerRun call that will redirect us back to ws
        assert(worker.getConnectionType() == Connection.IPC)
        ref = generateDataRef()
        task = worker.runTaskLocal(cid, ref, task_name, args)
        future = asyncio.ensure_future(task)
        datastore.putFuture(ref, future)
        # Broadcast to all raylet that we own the data
        msg = {"dataref": ref, "rayletid": self.getId()}
        response = await self.broadcast(self.API.SaveDataRef, msg)
        msg_obj = {"status": Status.SUCCESS, "dataref": ref}
        return msg_obj

    async def initWorker(self, data):
        rayletid = data["rayletid"]
        # Receive workerInit from ws. Save it and do not redirect it to ws
        worker = scheduler.addWorker(rayletws=rayletid)
        # No need to distribute task, as local raylet will do it in ipc.
        logging.info(f'Worker connect: {worker.getId()} from rayletid {rayletid}')
        msg_obj = {"status": Status.SUCCESS, "worker_id": worker.getId()}
        return msg_obj

    async def saveDataRef(self, data):
        ref, rayletid = data["dataref"], data["rayletid"]
        datastore.putLoc(ref, rayletid)
        msg_obj = {"status": Status.SUCCESS}
        return msg_obj

    async def getData(self, data):
        ref = data["dataref"]
        # unlike IPC case, when we get ws request, it should guarantee that the data is here.
        fut = datastore.getFuture(ref)
        if fut:
            response = await fut
            datastore.saveVal(ref, val=response.serialized_data, status=response.status)
        status, val = datastore.get(ref)
        msg_obj = {"status": status, "serialized_data": val}
        return msg_obj

def volpy_ws_create_session_runner(uuid, router, realm=None, is_main=False, logger=logging):
    global session
    realm = realm if realm else config.realm
    session = VolpyWS(ComponentConfig(realm, {}))
    session.init(uuid, is_main, logger=logging)
    session.addHandler()
    runner = ApplicationRunner(router, realm)
    return session, runner