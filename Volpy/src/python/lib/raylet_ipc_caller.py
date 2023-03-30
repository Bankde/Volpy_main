import asyncio
from grpc import aio
from .vgrpc import worker_pb2, worker_pb2_grpc
from .config import config

class Raylet_IPCCaller(object):
    '''
    IPCCaller module for raylet
    Calling from raylet to worker

    NOT a singleton, unlike caller in worker, raylet needs multiple ipccallers
    for each workers, so the instances will be handle by scheduler instead.
    '''
    def __init__(self):
        self.channel = None
        self.stub = None

    def connect(self, worker_ipc):
        self.channel = aio.insecure_channel(worker_ipc, options=[
            ('grpc.keepalive_time_ms', config.grpc_keep_alive),
            ('grpc.keepalive_timeout_ms', config.grpc_keep_alive_timeout)
        ])
        self.stub = worker_pb2_grpc.VolpyStub(self.channel)

    def addDisconnectCallback(self, func):
        self.channel.add_callback(func)

    async def waitReady(self, idx):
        await self.channel.channel_ready()

    async def InitTask(self, name, serialized_task, module_list):
        await self.channel.channel_ready()
        return await self.stub.InitTask(worker_pb2.TaskNameAndData(name=name, serialized_task=serialized_task, module_list=module_list))

    async def RunTask(self, cid, name, args):
        await self.channel.channel_ready()
        return await self.stub.RunTask(worker_pb2.IdTaskArgs(id=cid, name=name, args=args))