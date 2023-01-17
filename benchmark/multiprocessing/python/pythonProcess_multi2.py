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

def pi_monte_carlo():
    circle_points = 0
    square_points = 0
    for i in range(STEP // CORE):
        rand_x = rand.uniform(-1, 1)
        rand_y = rand.uniform(-1, 1)
        origin_dist = rand_x**2 + rand_y**2
        if origin_dist <= 1:
            circle_points += 1
        square_points += 1
    return (circle_points, square_points)

class TaskRunner(grpc_pb2_grpc.TaskServicer):
    async def RunPI(self, request, context):
        circles, squares = pi_monte_carlo()
        return grpc_pb2.Result(circles=circles, squares=squares)

async def serve(port):
    server = aio.server()
    grpc_pb2_grpc.add_TaskServicer_to_server(TaskRunner(), server)
    listen_addr = 'localhost:%d' % port
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()

def runServer(port):
    asyncio.run(serve(port))

async def test():
    ports = range(50000,50000+CORE)
    workers = [mp.Process(target=runServer, args=(port,), daemon=True)
               for port in ports]
    for worker in workers:
        worker.start()
    time.sleep(1) # Waiting for client to launch

    channels = []
    stubs = []
    for i in range(CORE):
        channel = aio.insecure_channel('localhost:%d' % ports[i])
        channels.append(channel)
        stub = grpc_pb2_grpc.TaskStub(channel)
        stubs.append(stub)

    t1 = timer()
    tasks = []
    for stub in stubs:
        tasks.append(stub.RunPI(None))
    responses = await asyncio.gather(*tasks)
    t2 = timer()

    circle_points = 0
    square_points = 0
    for response in responses:
        circle_points += response.circles
        square_points += response.squares

    for worker in workers:
        try:
            worker.kill()
        except Exception:
            pass
    
    pi = 4 * circle_points / square_points
    # print('PI result: {}'.format(pi))
    print('Time taken: {} ms'.format((t2-t1)*1000))
    return (t2-t1)*1000

if __name__ == '__main__':
    ts = []
    for i in range(10):
        ts.append(asyncio.run(test()))
    import json
    with open("result.json", "w") as f:
        json.dump(ts, f)