from .singleton import Singleton
from enum import Enum
from typing import List
from .raylet_ipc_caller import Raylet_IPCCaller as IPCCaller
import asyncio

import typing

class Connection(Enum):
    NONE = 0
    IPC = 1
    WS = 2

class Worker(object):
    def __init__(self, worker_name, idx : int, workeripc: int = None, rayletws: str = None):
        assert(not (workeripc and rayletws))
        self.worker_name = worker_name
        self.idx = idx
        if workeripc:
            self.connection = Connection.IPC
            self.workeripc = workeripc
            self.ipccaller = IPCCaller()
            self.ipccaller.connect(f'localhost:{workeripc}')
        elif rayletws:
            self.connection = Connection.WS
            self.rayletws = rayletws
            # TODO: redirect to rayletws
        else:
            raise

    def getConnectionType(self) -> Connection:
        return self.connection

    def getWSAddr(self) -> str:
        return self.rayletws
    
    def getIPCPort(self) -> int:
        return self.workeripc

    async def initTask(self, name, serialized_task):
        '''
        Blocking, waiting for the other side to finish initializing task
        '''
        if self.connection == Connection.IPC:
            return await self.ipccaller.InitTask(name, serialized_task)
        else:
            pass # TODO: redirect to rayletws

    async def runTask(self, cid, name, args):
        '''
        Not blocking, instead return coroutine
        '''
        if self.connection == Connection.IPC:
            return await self.ipccaller.RunTask(cid, name, args)
        else:
            pass # TODO: redirect to rayletws

class Scheduler(object, metaclass=Singleton):

    def __init__(self):
        self._workerList = []
        self._name2worker = {}
        self.workerNum = 0
        self.rr = 0
        self.tasks = {}

    def saveTask(self, taskname, serialized_task):
        self.tasks[taskname] = serialized_task

    def getAllTasks(self):
        return self.tasks

    def addWorker(self, workeripc=None, rayletws=None) -> Worker:
        '''
        Add and connect worker
        Either IPC (grpc) or Websocket (in case of different node)
        '''
        worker_name = f'worker-{self.workerNum+1}'
        worker = Worker(worker_name, self.workerNum, workeripc, rayletws)
        self._workerList.append(worker)
        self.workerNum += 1
        self._name2worker[worker_name] = worker
        return worker

    def getAllWorkers(self) -> List[Worker]:
        return self._workerList

    def getAllLocalWorkers(self) -> List[Worker]:
        return [worker for worker in self._workerList if worker.getConnectionType() == Connection.IPC ]

    def acquireWorker(self) -> Worker:
        # Round-robin
        cur_worker = self._workerList[self.rr % self.workerNum]
        self.rr += 1
        return cur_worker

    def getWorkerByName(self, worker_name) -> Worker:
        return self._name2worker[worker_name]

class Datastore(object, metaclass=Singleton):
    class VolpyData(object):
        def __init__(self, ref:str, loc:str = None, val=None, fut:asyncio.Future = None):
            self.ref = ref
            self.loc = loc # Currently not used unless we want to upgrade
            self.val = val
            self.fut = fut
            self.status = 0 if val else -1
            self.done = (fut is None)

    def __init__(self):
        self.dict = {}

    def get(self, ref:str) -> tuple[int, typing.Any]:
        '''
        Return the tuple of (status, val)
        '''
        try:
            obj = self.dict[ref]
            return (obj.status, obj.val)
        except Exception as e:
            return (3, None)

    def put(self, ref:str, val):
        obj = self.VolpyData(ref, val=val)
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

    