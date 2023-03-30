from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from .raylet_scheduler import Worker, Datastore
    from .raylet_ws import VolpyWS
    from .raylet_ipc_caller import Raylet_IPCCaller

from .util import Singleton
from .config import config
from enum import Enum

import logging
class Connection(Enum):
    NONE = 0
    IPC = 1
    WS = 2

raylet_ws: VolpyWS = None
IPCCaller: Raylet_IPCCaller = None
datastore: Datastore = None
def setup(l_raylet_ws, l_raylet_ipc_caller, l_datastore):
    global raylet_ws, IPCCaller, datastore
    raylet_ws = l_raylet_ws
    IPCCaller = l_raylet_ipc_caller
    datastore = l_datastore

class Worker_Connection(object):
    def __init__(self, workeripc: int=None, rayletid: str=None):
        assert(not (workeripc and rayletid))
        if workeripc:
            self.connectionType = Connection.IPC
            self.workeripc = workeripc
            self.ipccaller = IPCCaller()
            self.ipccaller.connect(f'localhost:{workeripc}')
        else:
            self.connectionType = Connection.WS
            # No need for self.rayletws, use the singleton instead.
            self.rayletid = rayletid
        
    def getConnectionType(self) -> Connection:
        return self.connectionType

    def getRayletId(self) -> str:
        return self.rayletid
    
    def getIPCPort(self) -> int:
        return self.workeripc

async def initTask(worker: Worker, name: str, serialized_task: bytes, module_list: list[str]):
    '''
    Blocking, waiting for the other side to finish initializing task
    '''
    if worker.connection.getConnectionType() == Connection.IPC:
        return await worker.connection.ipccaller.InitTask(name, serialized_task, module_list)
    else:
        # There shouldn't be any initTask send to worker via this method
        # initTask should be broadcasted through rayletws instead of iterating each worker.
        raise

async def runTaskLocal(worker: Worker, cid: str, ref: str, name: str, args: bytes):
    '''
    Run the task and do all routines when the task is finished.
    1. Save value into datastore
    2. Call FreeWorker to main raylet
    '''
    assert(worker.connection.getConnectionType() == Connection.IPC)
    response = await worker.connection.ipccaller.RunTask(cid, name, args)
    msg = {"cid": cid, "worker_id": worker.idx}
    datastore.saveVal(ref, val=response.serialized_data, status=response.status)
    if config.main:
        worker.unlock()
    else:
        # Send to main!! Not to the worker conn.
        await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.FreeWorker, msg)
    logging.info(f"Task done: {cid}")
    return response

async def runTaskRemote(worker: Worker, cid: str, name: str, args: bytes):
    '''
    UNLIKE runTaskLocal, we call the remote then we wait for the response status
    to ensure that the task is started, dataref is saved and broadcasted.
    '''
    assert(worker.connection.getConnectionType() == Connection.WS)
    msg = {"cid": cid, "worker_id": worker.idx, "task_name": name, "args": args}
    response = await raylet_ws.send(worker.connection.rayletid, raylet_ws.API.WorkerRun, msg)
    return response