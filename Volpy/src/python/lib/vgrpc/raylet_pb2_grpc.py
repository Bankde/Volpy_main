# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import raylet_pb2 as raylet__pb2
from . import volpy_pb2 as volpy__pb2


class VolpyStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitWorker = channel.unary_unary(
                '/raylet.Volpy/InitWorker',
                request_serializer=raylet__pb2.WorkerData.SerializeToString,
                response_deserializer=volpy__pb2.Status.FromString,
                )
        self.CreateTask = channel.unary_unary(
                '/raylet.Volpy/CreateTask',
                request_serializer=volpy__pb2.TaskNameAndData.SerializeToString,
                response_deserializer=volpy__pb2.Status.FromString,
                )
        self.SubmitTask = channel.unary_unary(
                '/raylet.Volpy/SubmitTask',
                request_serializer=volpy__pb2.IdTaskArgs.SerializeToString,
                response_deserializer=volpy__pb2.StatusWithDataRef.FromString,
                )
        self.GetAllTasks = channel.unary_unary(
                '/raylet.Volpy/GetAllTasks',
                request_serializer=volpy__pb2.Empty.SerializeToString,
                response_deserializer=raylet__pb2.AllTasks.FromString,
                )
        self.Get = channel.unary_unary(
                '/raylet.Volpy/Get',
                request_serializer=volpy__pb2.DataRef.SerializeToString,
                response_deserializer=volpy__pb2.StatusWithData.FromString,
                )
        self.Put = channel.unary_unary(
                '/raylet.Volpy/Put',
                request_serializer=volpy__pb2.Data.SerializeToString,
                response_deserializer=volpy__pb2.StatusWithDataRef.FromString,
                )


class VolpyServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitWorker(self, request, context):
        """Worker
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateTask(self, request, context):
        """Task
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SubmitTask(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllTasks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Get(self, request, context):
        """DataStore
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Put(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VolpyServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InitWorker': grpc.unary_unary_rpc_method_handler(
                    servicer.InitWorker,
                    request_deserializer=raylet__pb2.WorkerData.FromString,
                    response_serializer=volpy__pb2.Status.SerializeToString,
            ),
            'CreateTask': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateTask,
                    request_deserializer=volpy__pb2.TaskNameAndData.FromString,
                    response_serializer=volpy__pb2.Status.SerializeToString,
            ),
            'SubmitTask': grpc.unary_unary_rpc_method_handler(
                    servicer.SubmitTask,
                    request_deserializer=volpy__pb2.IdTaskArgs.FromString,
                    response_serializer=volpy__pb2.StatusWithDataRef.SerializeToString,
            ),
            'GetAllTasks': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllTasks,
                    request_deserializer=volpy__pb2.Empty.FromString,
                    response_serializer=raylet__pb2.AllTasks.SerializeToString,
            ),
            'Get': grpc.unary_unary_rpc_method_handler(
                    servicer.Get,
                    request_deserializer=volpy__pb2.DataRef.FromString,
                    response_serializer=volpy__pb2.StatusWithData.SerializeToString,
            ),
            'Put': grpc.unary_unary_rpc_method_handler(
                    servicer.Put,
                    request_deserializer=volpy__pb2.Data.FromString,
                    response_serializer=volpy__pb2.StatusWithDataRef.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'raylet.Volpy', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Volpy(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InitWorker(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raylet.Volpy/InitWorker',
            raylet__pb2.WorkerData.SerializeToString,
            volpy__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raylet.Volpy/CreateTask',
            volpy__pb2.TaskNameAndData.SerializeToString,
            volpy__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SubmitTask(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raylet.Volpy/SubmitTask',
            volpy__pb2.IdTaskArgs.SerializeToString,
            volpy__pb2.StatusWithDataRef.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetAllTasks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raylet.Volpy/GetAllTasks',
            volpy__pb2.Empty.SerializeToString,
            raylet__pb2.AllTasks.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Get(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raylet.Volpy/Get',
            volpy__pb2.DataRef.SerializeToString,
            volpy__pb2.StatusWithData.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Put(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raylet.Volpy/Put',
            volpy__pb2.Data.SerializeToString,
            volpy__pb2.StatusWithDataRef.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
