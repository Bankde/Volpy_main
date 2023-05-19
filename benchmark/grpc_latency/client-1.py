import multiprocessing as mp
from numpy import random as rand
from timeit import default_timer as timer
from vgrpc import grpc_pb2_grpc, grpc_pb2
import asyncio
from grpc import aio
import time
import os

async def test():
    channel = aio.insecure_channel('localhost:50000')
    stub = grpc_pb2_grpc.TaskStub(channel)

    t1 = timer()
    r = await stub.Ping(None)
    t2 = timer()
    time1 = (t2-t1)*1000
    # print("First: %.3f" % (time1))

    time.sleep(1)

    t1 = timer()
    r = await stub.Ping(None)
    t2 = timer()
    time2 = (t2-t1)*1000
    # print("Second: %.3f" % (time2))

    t1 = timer()
    for i in range(100):
        r = await stub.Ping(None)
    t2 = timer()
    time3 = (t2-t1)*1000/100
    # print("After: %.3f" % (time3))
    return (time1,time2,time3)

if __name__ == '__main__':
    tt1, tt2, tt3 = [], [], []
    for i in range(100):
      t1,t2,t3 = asyncio.run(test())
      tt1.append(t1)
      tt2.append(t2)
      tt3.append(t3)
    print(tt1)
    print(tt2)
    print(tt3)