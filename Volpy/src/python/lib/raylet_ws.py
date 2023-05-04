from .simple_ws import SimpleWS
from .config import config
from autobahn.wamp.types import ComponentConfig
from autobahn.asyncio.wamp import ApplicationRunner
from .raylet_scheduler import scheduler, datastore, Connection, SharedLogic
import base64

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
        GetWorkerMeta = 15
        SaveWorkerMeta = 16

        SaveDataRef = 21
        GetData = 22
        GetDataMeta = 23

    def addHandler(self):
        # {"cid": int, "worker_id": str, "task_name": str, "args": bytes}
        # ret: {"status": int, "dataref": str}
        # A command to run the task on this node. Behave like running task with ipc.
        # Will broadcast dataref to other nodes with its rayletid.
        # Return dataref, the result data of the task will store locally.
        self.setCallback(self.API.WorkerRun, self.workerRun)
        # {"dataref": str}
        # ret: {"status": int, "serialized_data": bytes}
        # Get data from ref
        self.setCallback(self.API.GetData, self.getData)

        '''
        API for main volpy
        '''
        # {"cid": int, "task_name": str, "args": bytes}
        # ret: {"status": int, "worker_id": str} 
        # Acquire worker from main raylet. Lock the worker.
        self.setCallback(self.API.AcquireWorker, self.acquireWorker)
        # {"cid": int, "worker_id": str"}
        # ret: {"status": int}
        # Unlock the worker.
        self.setCallback(self.API.FreeWorker, self.freeWorker)
        # {"rayletid": str}
        # ret: {"status": int, "worker_id": str}
        # Tell the main raylet that new worker has been connected.
        # The scheduler will save worker in the list and return the new assigned Id
        self.setCallback(self.API.InitWorker, self.initWorker)

        '''
        API to maintain shared data between all raylets
        - task
        - worker meta
        - dataref meta
        '''
        # {"task_name": str, "serialized_task": bytes, "module_list": [str]}
        # ret: {"status": int}
        self.setCallback(self.API.CreateTask, self.createTask)
        # {}
        # ret: {"all_tasks": List[Dict<task_name, serialized_task, List[str]>]}
        # Return all tasks
        self.setCallback(self.API.GetAllTasks, self.getAllTasks)
        # {}
        # ret: {"all_workers": List[Dict<id, rayletid>]}
        # Return all worker metadata
        self.setCallback(self.API.GetWorkerMeta, self.getWorkerMeta)
        # {"worker_id": str, "rayletid": str}
        # ret: {"status": int}
        # Tell raylet that new worker is registered into the system
        self.setCallback(self.API.SaveWorkerMeta, self.saveWorkerMeta)
        # {"dataref": str, "rayletid": str}
        # ret: {"status": int}
        # Tell raylet that the pair of dataRef and its location
        self.setCallback(self.API.SaveDataRef, self.saveDataRef)
        # {}
        # ret: {"all_data": List[Dict<dataref, rayletid>]}
        # Return all data metadata
        self.setCallback(self.API.GetDataMeta, self.getDataMeta)

    def addDataCallback(self):
        def recvConversion(data):
            if data == None:
                return data
            for key in ["serialized_task", "serialized_data", "args"]:
                if key in data:
                    data[key] = base64.b64decode(data[key])
            if "all_tasks" in data:
                for i in range(len(data["all_tasks"])):
                    data["all_tasks"][i]["serialized_task"] = base64.b64decode(data["all_tasks"][i]["serialized_task"])
            return data
        def sendConversion(data):
            if data == None:
                return data
            for key in ["serialized_task", "serialized_data", "args"]:
                if key in data:
                    # byte --[base64]-->  byte --[decode_to_str]--> str
                    data[key] = (base64.b64encode(data[key])).decode('ascii')
            if "all_tasks" in data:
                for i in range(len(data["all_tasks"])):
                    data["all_tasks"][i]["serialized_task"] = (base64.b64encode(data["all_tasks"][i]["serialized_task"])).decode('ascii')
            return data
        self.dataRecvCallback = recvConversion
        self.dataSendCallback = sendConversion

    async def createTask(self, data):
        """
        Receive CreateTask from raylet (either main/not) ws.
        Raylet has to broadcast the task to all workers (IPC).
        """
        task_name, serialized_task, module_list = data["task_name"], data["serialized_task"], data["module_list"]
        logging.info(f'Recv CreateTask: {task_name}')
        scheduler.saveTask(task_name, serialized_task, module_list)
        # Broadcast to all worker ipc
        workers = scheduler.getAllLocalWorkers()
        if config.main:
            logging.warn(f'Main raylet receive createTask from WS (ok if you attach REPL to non-main)')
        tasks = []
        for worker in workers:
            task = SharedLogic.initTask(worker, task_name, serialized_task=serialized_task, module_list=module_list)
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        msg_obj = {"status": Status.SUCCESS}
        return msg_obj
    
    async def getAllTasks(self, data):
        """
        Return all of the declared tasks
        """
        all_tasks = scheduler.getAllTasks()
        all_tasks_arr = []
        for task in all_tasks:
            serialized_task, module_list = all_tasks[task]
            all_tasks_arr.append({"task_name": task, "serialized_task": serialized_task, "module_list": module_list})
        msg_obj = {"all_tasks": all_tasks_arr}
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
        # There shouldn't be a workerRun call that will redirect us back to remote ws
        assert(worker.getConnectionType() == Connection.IPC)
        ref = generateDataRef()
        logging.info(f'Generate ref: {cid} {ref}')
        task = SharedLogic.runTaskLocal(session, worker, cid, ref, task_name, args)
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
        worker = scheduler.addWorker(connection=rayletid, connectionType=Connection.WS)
        # No need to distribute task, as local raylet will do it in ipc.
        logging.info(f'Worker connect (main,ws): {worker.getId()} rayletid {rayletid}')
        msg_obj = {"status": Status.SUCCESS, "worker_id": worker.getId()}
        return msg_obj

    async def getWorkerMeta(self, data):
        # This API should be called before that node init any workers.
        workers = scheduler.getAllWorkers()
        worker_meta = []
        for worker in workers:
            if worker.connectionType == Connection.IPC:
                worker_meta.append({"id": worker.getId(), "rayletid": self.getId()})
            else:
                worker_meta.append({"id": worker.getId(), "rayletid": worker.connection})
        msg_obj = {"all_workers": worker_meta}
        return msg_obj

    async def saveWorkerMeta(self, data):
        worker_id, rayletid = data["worker_id"], data["rayletid"]
        if (scheduler.getWorkerById(worker_id) == None):
            scheduler.addWorkerWithId(worker_id, rayletid, Connection.WS)
        msg_obj = {"status": Status.SUCCESS}
        return msg_obj

    async def saveDataRef(self, data):
        ref, rayletid = data["dataref"], data["rayletid"]
        logging.info(f'Recv dataref: {ref} {rayletid}')
        datastore.putLoc(ref, rayletid)
        msg_obj = {"status": Status.SUCCESS}
        return msg_obj

    async def getData(self, data):
        ref = data["dataref"]
        logging.info(f'Recv ws Get: {ref}')
        # unlike IPC case, when we get ws request, it should guarantee that the data is here.
        fut = datastore.getFuture(ref)
        if fut:
            response = await fut
            datastore.saveVal(ref, val=response.serialized_data, status=response.status)
        status, val = datastore.get(ref)
        msg_obj = {"status": status, "serialized_data": val}
        return msg_obj
    
    async def getDataMeta(self, data):
        all_data = datastore.dict
        data_meta = []
        for ref in all_data:
            data = all_data[ref]
            if data.loc:
                data_meta.append({"dataref": ref, "rayletid": data.loc})
            else:
                # Either future (still running) or has val (finished)
                data_meta.append({"dataref": ref, "rayletid": self.getId()})
        msg_obj = {"all_metadata": data_meta}
        return msg_obj

def volpy_ws_create_session_runner(uuid, router, realm=None, is_main=False, logger=logging):
    global session
    realm = realm if realm else config.realm
    session = VolpyWS(ComponentConfig(realm, {}))
    session.init(uuid, is_main, logger=logging)
    session.addHandler()
    session.addDataCallback()
    runner = ApplicationRunner(router, realm)
    return session, runner