from grpc import aio
from .vgrpc import raylet_pb2, raylet_pb2_grpc
from .singleton import Singleton
from .config import config

class Worker_IPCCaller(object, metaclass=Singleton):
    '''
    IPCCaller module for worker
    Calling from worker/repl to raylet
    '''
    def __init__(self):
        self.rayletipc = None
        self.channel = None
        self.stub = None

    def connect(self, rayletipc):
        self.rayletipc = rayletipc
        self.channel = aio.insecure_channel(self.rayletipc, options=[
            ('grpc.keepalive_time_ms', config.grpc_keep_alive),
            ('grpc.keepalive_timeout_ms', config.grpc_keep_alive_timeout)
        ])
        self.stub = raylet_pb2_grpc.VolpyStub(self.channel)

    async def waitReady(self):
        await self.channel.channel_ready()

    async def CreateTask(self, name, serialized_task):
        return await self.stub.CreateTask(raylet_pb2.TaskNameAndCode(name=name, serialized_task=serialized_task))

    async def SubmitTask(self, cid, name, args):
        return await self.stub.SubmitTask(raylet_pb2.IdTaskArgs(id=cid, name=name, args=args))

    async def InitWorker(self, port):
        return await self.stub.InitWorker(raylet_pb2.WorkerData(port=port))

ipc_caller = Worker_IPCCaller()