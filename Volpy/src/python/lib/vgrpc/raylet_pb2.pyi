import volpy_pb2 as _volpy_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

from volpy_pb2 import TaskNameAndCode
from volpy_pb2 import IdTaskArgs
from volpy_pb2 import Status
from volpy_pb2 import DataRef
from volpy_pb2 import StatusWithDataRef
from volpy_pb2 import Data
from volpy_pb2 import StatusWithData
from volpy_pb2 import Empty
DESCRIPTOR: _descriptor.FileDescriptor

class AllTasks(_message.Message):
    __slots__ = ["taskmap"]
    class TaskmapEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bytes
        def __init__(self, key: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
    TASKMAP_FIELD_NUMBER: _ClassVar[int]
    taskmap: _containers.ScalarMap[str, bytes]
    def __init__(self, taskmap: _Optional[_Mapping[str, bytes]] = ...) -> None: ...

class WorkerData(_message.Message):
    __slots__ = ["port"]
    PORT_FIELD_NUMBER: _ClassVar[int]
    port: str
    def __init__(self, port: _Optional[str] = ...) -> None: ...
