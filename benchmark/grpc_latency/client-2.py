import multiprocessing as mp
from numpy import random as rand
from timeit import default_timer as timer
from vgrpc import grpc_pb2_grpc, grpc_pb2
import asyncio
from grpc import aio
import time
import os

async def test():
    channel = aio.insecure_channel('localhost:50000', options=[
        ('grpc.keepalive_time_ms', 10000),
        ('grpc.keepalive_timeout_ms', 2000)
    ])
    stub = grpc_pb2_grpc.TaskStub(channel)

    await channel.channel_ready()

    t1 = timer()
    r = await stub.Ping(None)
    t2 = timer()
    print("First: %.3f" % ((t2-t1)*1000))

    time.sleep(1)

    await channel.channel_ready()

    t1 = timer()
    r = await stub.Ping(None)
    t2 = timer()
    print("Second: %.3f" % ((t2-t1)*1000))

    t1 = timer()
    r = await stub.Ping(None)
    t2 = timer()
    print("After: %.3f" % ((t2-t1)*1000))

if __name__ == '__main__':
    for i in range(10):
        asyncio.run(test())