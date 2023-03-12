from .vgrpc import worker_pb2_grpc, worker_pb2
import asyncio
from grpc import aio
import codepickle
import cloudpickle

from . import worker_executor
import logging

from .util import Status

class TaskRunner(worker_pb2_grpc.VolpyServicer):
    async def InitTask(self, request, context):
        task_name = request.name
        logging.info(f'Recv InitTask: {task_name}')
        serialized_task = request.serialized_task
        try:
            worker_executor.initTask(task_name, serialized_task)
        except:
            return worker_pb2.Status(status=Status.SERIALIZATION_ERROR)
        return worker_pb2.Status(status=Status.SUCCESS)

    async def RunTask(self, request, context):
        cid = request.id
        task_name = request.name
        logging.info(f'Recv RunTask: {cid} {task_name}')
        args = request.args
        try:
            data = await worker_executor.executeTask(task_name, args)
            return worker_pb2.StatusWithData(status=Status.SUCCESS, serialized_data=data)
        except worker_executor.ExecutionError:
            return worker_pb2.StatusWithData(status=Status.EXECUTION_ERROR, serialized_data=b"")
        except worker_executor.SerializationError:
            return worker_pb2.StatusWithData(status=Status.SERIALIZATION_ERROR, serialized_data=b"")

class WorkerIPCServer(object):
    def __init__(self, port):
        self.server = aio.server()
        worker_pb2_grpc.add_VolpyServicer_to_server(TaskRunner(), self.server)
        self.port = self.server.add_insecure_port(port)

    def getRunningPort(self):
        return self.port

    async def run(self):
        await self.server.start()