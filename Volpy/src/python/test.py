import lib.vgrpc.worker_pb2_grpc as worker_pb2_grpc
import lib.vgrpc.worker_pb2 as worker_pb2
import asyncio
from grpc import aio 

def test1():
    return 1

def test2(a):
    return 1+a
class TaskRunner(worker_pb2_grpc.VolpyServicer):
    async def InitTask(self, request, context):
        task_name = request.name
        serialized_task = request.serialized_task
        # print(task_name, serialized_task)
        # print("done")
        return worker_pb2.Status(status=0)

    async def RunTask(self, request, context):
        id = request.id
        task_name = request.name
        args = request.args
        # print(task_name, args)
        return worker_pb2.StatusWithData(status=0, serialized_data=b'test')

async def serve():
    server = aio.server()
    worker_pb2_grpc.add_VolpyServicer_to_server(TaskRunner(), server)
    listen_addr = 'localhost:50051'
    server.add_insecure_port(listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
