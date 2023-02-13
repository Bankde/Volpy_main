from .vgrpc import raylet_pb2_grpc, raylet_pb2
from .vgrpc import worker_pb2_grpc, worker_pb2
import asyncio
from grpc import aio 
from .raylet_scheduler import scheduler, datastore
from .config import config

import logging
import uuid

def generateDataRef():
    return str(uuid.uuid4())

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
        # If main raylet, also broadcast to all raylets through ws
        if config.main:
            pass # TODO: broadcast to all raylets
        # Broadcast to all worker process
        for worker in workers:
            task = worker.initTask(task_name, serialized_task=serialized_task)
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return raylet_pb2.Status(status=0)

    async def SubmitTask(self, request, context):
        cid = request.id
        task_name = request.name
        logging.info(f'Recv SubmitTask: {cid} {task_name}')
        args = request.args
        ref = generateDataRef()
        worker = scheduler.acquireWorker()
        task = worker.runTask(cid, task_name, args)
        future = asyncio.ensure_future(task)
        datastore.putFuture(ref, future)
        return raylet_pb2.DataRef(dataref=ref)

    async def InitWorker(self, request, context):
        # Receive directly from worker, save the IPC into the raylet.
        # If this is not main raylet, then also inform main raylet through ws
        workeripc = request.port
        worker = scheduler.addWorker(workeripc=workeripc)
        if not config.main:
            pass # TODO: SEND TO MAIN RAYLET
        # Distribute all existing tasks to the new worker
        all_tasks = scheduler.getAllTasks()
        if len(all_tasks) > 0:
            async_tasks = []
            for task_name, serialized_task in all_tasks.items():
                t = worker.initTask(task_name, serialized_task=serialized_task)
                async_tasks.append(t)
            responses = await asyncio.gather(*async_tasks) # Not sure what to do with the responses if error yet, but it should not
        # Logging
        logging.info(f'Worker connect: {worker.worker_name} with port {workeripc}')
        return raylet_pb2.Status(status=0)

    async def Get(self, request, context):
        '''
        This API is blocking until the task is finished and return the result.
        '''
        ref = request.dataref
        fut = datastore.getFuture(ref)
        if fut:
            response = await fut
            datastore.saveVal(ref, val=response.serialized_data, status=response.status)
        status, val = datastore.get(ref)
        return raylet_pb2.StatusWithData(status=status, serialized_data=val)

    async def Put(self, request, context):
        val = request.serialized_data
        ref = generateDataRef()
        datastore.put(ref, val)
        return raylet_pb2.DataRef(dataref=ref)

class RayletIPCServer(object):
    def __init__(self, port):
        self.server = aio.server()
        raylet_pb2_grpc.add_VolpyServicer_to_server(TaskRunner(), self.server)
        self.port = self.server.add_insecure_port(port)

    def getRunningPort(self):
        return self.port

    async def run(self):
        await self.server.start()