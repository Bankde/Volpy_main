import volpy_pb2 as _volpy_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

from volpy_pb2 import TaskNameAndData
from volpy_pb2 import IdTaskArgs
from volpy_pb2 import Status
from volpy_pb2 import DataRef
from volpy_pb2 import StatusWithDataRef
from volpy_pb2 import Data
from volpy_pb2 import StatusWithData
from volpy_pb2 import Empty
DESCRIPTOR: _descriptor.FileDescriptor

class AllTasks(_message.Message):
    __slots__ = ["all_tasks"]
    ALL_TASKS_FIELD_NUMBER: _ClassVar[int]
    all_tasks: _containers.RepeatedCompositeFieldContainer[_volpy_pb2.TaskNameAndData]
    def __init__(self, all_tasks: _Optional[_Iterable[_Union[_volpy_pb2.TaskNameAndData, _Mapping]]] = ...) -> None: ...

class WorkerData(_message.Message):
    __slots__ = ["port"]
    PORT_FIELD_NUMBER: _ClassVar[int]
    port: str
    def __init__(self, port: _Optional[str] = ...) -> None: ...
