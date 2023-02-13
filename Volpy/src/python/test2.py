import lib.vgrpc.worker_pb2_grpc as worker_pb2_grpc
import lib.vgrpc.worker_pb2 as worker_pb2
import asyncio
from grpc import aio
import time

async def run():
    async with aio.insecure_channel('localhost:50051') as channel:
        while True:
            tasks = []
            stub = worker_pb2_grpc.VolpyStub(channel)
            tasks.append(stub.InitTask(worker_pb2.TaskNameAndCode(name=b"taskName", serialized_task=b"code")))
            responses = await asyncio.gather(*tasks)
            for response in responses:
                print("Response: %d" % response.status)
            time.sleep(1)

asyncio.run(run())