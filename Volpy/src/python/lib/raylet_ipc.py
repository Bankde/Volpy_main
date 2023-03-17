from .vgrpc import raylet_pb2_grpc, raylet_pb2
from .vgrpc import worker_pb2_grpc, worker_pb2
import asyncio
from grpc import aio 
from .config import config
from .raylet_scheduler import scheduler, datastore, Connection, fire_and_forget_task

from .util import Status, generateDataRef

import logging
import uuid

def setup():
    global raylet_ws
    from .raylet_ws import session as raylet_ws

class TaskRunner(raylet_pb2_grpc.VolpyServicer):
    async def CreateTask(self, request, context):
        """
        Receive CreateTask from driver/worker.
        Raylet has to broadcast the task to all workers (IPC) and other raylets (websocket).
        """
        task_name = request.name
        logging.info(f'Recv CreateTask: {task_name}')
        serialized_task = request.serialized_task
        scheduler.saveTask(task_name, serialized_task)
        workers = scheduler.getAllWorkers()
        tasks = []
        # Broadcast to all raylets through ws
        msg = {"task_name": task_name, "serialized_task": serialized_task}
        task = raylet_ws.broadcast(raylet_ws.API.CreateTask, msg)
        tasks.append(task)
        # Broadcast to all worker process
        for worker in workers:
            # For other rayletws connection, let other nodes handle by themselves.
            if worker.getConnectionType() == Connection.IPC:
                task = worker.initTask(task_name, serialized_task=serialized_task)
                tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return raylet_pb2.Status(status=Status.SUCCESS)

    async def SubmitTask(self, request, context):
        cid, task_name, args = request.id, request.name, request.args
        logging.info(f'Recv SubmitTask: {cid} {task_name}')
        if config.main:
            worker = scheduler.acquireWorker()
        else:
            # Acquire worker from main raylet scheduler.
            msg = {"cid": cid, "task_name": task_name, "args": args}
            response = await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.AcquireWorker, msg)
            worker_id = response.worker_id
            worker = scheduler.getWorkerById(worker_id)
        if worker == None:
            logging.info(f'All worker busy: {cid}')
            return raylet_pb2.StatusWithDataRef(status=Status.WORKER_BUSY, dataref="")

        logging.info(f'Worker acquire: {cid} {worker.getId()}')
        if worker.getConnectionType() == Connection.IPC:
            ref = generateDataRef()
            task = worker.runTaskLocal(cid, ref, task_name, args)
            future = asyncio.ensure_future(task)
            datastore.putFuture(ref, future)
            # Broadcast to all raylet that we own the data
            msg = {"dataref": ref, "rayletid": raylet_ws.getId()}
            response = await raylet_ws.broadcast(raylet_ws.API.SaveDataRef, msg)
        else:
            response = await worker.runTaskRemote(cid, task_name, args)
            status, ref = response.status, response.dataref
        logging.info(f'Generate ref: {cid} {ref}')
        return raylet_pb2.StatusWithDataRef(status=Status.SUCCESS, dataref=ref)

    async def InitWorker(self, request, context):
        # Receive directly from worker, save the IPC into the raylet.
        # If this is not main raylet, then also inform main raylet through ws
        workeripc = request.port
        if config.main:
            worker = scheduler.addWorker(workeripc=workeripc)
        else:
            msg = {"rayletid": raylet_ws.getId()}
            response = await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.InitWorker, msg)
            status, new_worker_id = response.status, response.worker_id
            # We use the id designated from main, however the worker is connected to our local as ipc
            # So we still set ipc here; the rayletws will only be set in main raylet.
            worker = scheduler.addWorkerWithId(new_worker_id, workeripc=workeripc)
        return raylet_pb2.Status(status=Status.SUCCESS)
    
    async def GetAllTasks(self, request, context):
        all_tasks = scheduler.getAllTasks()
        return raylet_pb2.AllTasks(taskmap=all_tasks)

    async def Get(self, request, context):
        '''
        This API is blocking until the task is finished and return the result.
        '''
        ref = request.dataref
        fut = datastore.getFuture(ref)
        if fut:
            response = await fut
        status, val = datastore.get(ref)
        if status == Status.DATA_ON_OTHER:
            rayletid = val
            msg = {"dataref": ref}
            response = await raylet_ws.send(rayletid, raylet_ws.API.GetData, msg)
            status, val = response.status, response.serialized_data
            # Call WS to get data from other raylet then save it locally
        return raylet_pb2.StatusWithData(status=status, serialized_data=val)

    async def Put(self, request, context):
        val = request.serialized_data
        ref = generateDataRef()
        datastore.put(ref, val)
        # Broadcast dataref to all raylets
        msg = {"dataref": ref, "rayletid": raylet_ws.getId()}
        response = await raylet_ws.broadcast(raylet_ws.API.SaveDataRef, msg)
        return raylet_pb2.StatusWithDataRef(status=Status.SUCCESS, dataref=ref)

class RayletIPCServer(object):
    def __init__(self, port):
        self.server = aio.server()
        raylet_pb2_grpc.add_VolpyServicer_to_server(TaskRunner(), self.server)
        self.port = self.server.add_insecure_port(port)

    def getRunningPort(self):
        return self.port

    async def run(self):
        await self.server.start()