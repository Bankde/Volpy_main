import volpy_pb2 as _volpy_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

from volpy_pb2 import TaskNameAndCode
from volpy_pb2 import IdTaskArgs
from volpy_pb2 import Status
from volpy_pb2 import DataRef
from volpy_pb2 import StatusWithData
from volpy_pb2 import Data
DESCRIPTOR: _descriptor.FileDescriptor

class WorkerData(_message.Message):
    __slots__ = ["port"]
    PORT_FIELD_NUMBER: _ClassVar[int]
    port: str
    def __init__(self, port: _Optional[str] = ...) -> None: ...
