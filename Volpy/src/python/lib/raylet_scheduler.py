from __future__ import annotations

from .singleton import Singleton
from enum import Enum
from typing import List, Dict, Any
import asyncio

import logging
from .config import config
from .util import Status

class Connection(Enum):
    NONE = 0
    IPC = 1
    WS = 2
    THREAD = 3

class Worker(object):
    def __init__(self, idx : str, connection, connectionType: Connection):
        '''
        Connection should be one of the following:
        - ConnectionType:WS - rayletid
        - ConnectionType:IPC - ipc_caller instance
        '''
        self.idx = idx
        self.locked = False
        self.connection = connection
        self.connectionType = connectionType

    def lock(self):
        self.locked = True
        logging.info(f'Worker lock: {self.getId()}')

    def unlock(self):
        logging.info(f'Worker unlock: {self.getId()}')
        self.locked = False

    def isLocked(self) -> bool:
        return self.locked

    def getId(self) -> str:
        return self.idx
    
    def getConnectionType(self) -> Connection:
        return self.connectionType
    
class Scheduler(object, metaclass=Singleton):

    def __init__(self):
        self._workerList: List[Worker] = []
        self._id2worker: Dict[int, Worker] = {}
        self.workerNum = 0
        self.rr = 0
        self.tasks: Dict[str, tuple[bytes, List[str]]] = {}

    def saveTask(self, taskname: str, serialized_task: bytes, module_list: List[str]):
        self.tasks[taskname] = (serialized_task, module_list)

    def getAllTasks(self) -> Dict[str, tuple[bytes, List[str]]]:
        return self.tasks

    def addWorker(self, connection, connectionType: Connection) -> Worker:
        '''
        Add and connect worker
        Either IPC (grpc) or WebsocketId (in case of different node)
        '''
        worker_id = str(self.workerNum)
        worker = Worker(worker_id, connection, connectionType)
        self._workerList.append(worker)
        self.workerNum += 1
        self._id2worker[worker_id] = worker
        return worker

    def addWorkerWithId(self, worker_id: str, connection, connectionType: Connection) -> Worker:
        '''
        Add and connect worker with Id
        Use this API when Id is assigned from the main raylet.
        Either IPC (grpc) or WebsocketId (in case of different node)
        '''
        worker_id = str(worker_id)
        worker = Worker(worker_id, connection, connectionType)
        self.workerNum += 1
        self._workerList.append(worker)
        self._id2worker[worker_id] = worker
        return worker

    def getAllWorkers(self) -> List[Worker]:
        return self._workerList

    def getAllLocalWorkers(self) -> List[Worker]:
        return [worker for worker in self._workerList if worker.getConnectionType() == Connection.IPC ]

    def acquireWorker(self) -> Worker:
        '''
        Acquire the free worker to perform task.
        The worker will be locked.
        '''
        # Round-robin
        for i in range(self.workerNum):
            acq_id = self.rr % self.workerNum
            cur_worker = self._workerList[acq_id]
            self.rr += 1
            if cur_worker.isLocked() == False:
                cur_worker.lock()
                return cur_worker
        return None
    
    def freeWorker(self, worker_id:str):
        worker = self.getWorkerById(worker_id)
        worker.unlock()

    def getWorkerById(self, worker_id: str) -> Worker:
        return self._id2worker.get(worker_id, None)

class Datastore(object, metaclass=Singleton):
    class VolpyData(object):
        def __init__(self, ref:str, loc:str = None, val=None, fut:asyncio.Future = None):
            self.ref = ref
            self.loc = loc
            self.val = val
            self.fut = fut
            self.status = 0 if val else -1
            self.done = (fut is None and loc is None)

    def __init__(self):
        self.dict = {}

    def get(self, ref:str) -> tuple[int, Any]:
        '''
        Return the tuple of (status, val)
        '''
        if not ref in self.dict:
            return (Status.DATA_NOT_FOUND, None)
        
        obj = self.dict[ref]
        if obj.val != None:
            return (obj.status, obj.val)
        
        assert(obj.loc != None)
        return (Status.DATA_ON_OTHER, obj.loc)

    def put(self, ref:str, val):
        obj = self.VolpyData(ref, val=val)
        self.dict[ref] = obj

    def putLoc(self, ref:str, loc):
        obj = self.VolpyData(ref, loc=loc)
        self.dict[ref] = obj

    def putFuture(self, ref:str, fut:asyncio.Future):
        obj = self.VolpyData(ref, fut=fut)
        self.dict[ref] = obj

    def isDone(self, ref:str) -> bool:
        return self.dict[ref].done

    def getFuture(self, ref:str) -> asyncio.Future:
        obj = self.dict[ref]
        if obj.done == True:
            return None
        else:
            return self.dict[ref].fut

    def saveVal(self, ref:str, val, status=0):
        obj = self.dict[ref]
        obj.val = val
        obj.status = status
        obj.done = True

scheduler = Scheduler()
datastore = Datastore()

forget_background_tasks = set()
def fire_and_forget_task(coro):
    task = asyncio.create_task(coro)
    forget_background_tasks.add(task)
    task.add_done_callback(forget_background_tasks.discard)
    
class SharedLogic():
    @staticmethod
    async def initTask(worker: Worker, task_name: str, serialized_task: bytes, module_list: list[str]):
        '''
        Blocking, waiting for the other side to finish initializing task
        '''
        if worker.getConnectionType() == Connection.IPC:
            ipccaller = worker.connection
            return await ipccaller.InitTask(task_name, serialized_task, module_list)
        else:
            # There shouldn't be any initTask send to worker via this method
            # initTask should be broadcasted through rayletws instead of iterating each worker.
            raise

    @staticmethod
    async def runTaskLocal(raylet_ws, worker: Worker, cid: str, ref: str, task_name: str, args: bytes):
        '''
        Run the task and do all routines when the task is finished.
        1. Save value into datastore
        2. Call FreeWorker to main raylet
        '''
        assert(worker.getConnectionType() == Connection.IPC)
        ipccaller = worker.connection
        response = await ipccaller.RunTask(cid, task_name, args)
        msg = {"cid": cid, "worker_id": worker.idx}
        datastore.saveVal(ref, val=response.serialized_data, status=response.status)
        if config.main:
            worker.unlock()
        else:
            # Send to main!! Not to the worker conn.
            await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.FreeWorker, msg)
        logging.info(f"Task done: {cid}")
        return response

    @staticmethod
    async def runTaskRemote(raylet_ws, worker: Worker, cid: str, task_name: str, args: bytes):
        '''
        UNLIKE runTaskLocal, we call the remote then we wait for the response status
        to ensure that the task is started, dataref is saved and broadcasted.
        '''
        assert(worker.getConnectionType() == Connection.WS)
        msg = {"cid": cid, "worker_id": worker.idx, "task_name": task_name, "args": args}
        response = await raylet_ws.send(worker.connection, raylet_ws.API.WorkerRun, msg)
        return response