import multiprocessing as mp
from numpy import random as rand
from timeit import default_timer as timer
from vgrpc import grpc_pb2_grpc, grpc_pb2
import asyncio
from grpc import aio
import time
import os

CORE = 4
STEP = int(os.getenv("SIZE", 1000 ** 2))

class TaskRunner(grpc_pb2_grpc.TaskServicer):
    async def Ping(self, request, context):
        return grpc_pb2.Result(status=1)

async def serve(port):
    server = aio.server()
    grpc_pb2_grpc.add_TaskServicer_to_server(TaskRunner(), server)
    listen_addr = 'localhost:%d' % port
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()

def runServer(port):
    asyncio.run(serve(port))

if __name__ == '__main__':
    runServer(50000)