from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Result(_message.Message):
    __slots__ = ["circles", "squares"]
    CIRCLES_FIELD_NUMBER: _ClassVar[int]
    SQUARES_FIELD_NUMBER: _ClassVar[int]
    circles: int
    squares: int
    def __init__(self, circles: _Optional[int] = ..., squares: _Optional[int] = ...) -> None: ...
