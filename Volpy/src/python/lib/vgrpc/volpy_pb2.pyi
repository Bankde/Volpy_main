from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Data(_message.Message):
    __slots__ = ["serialized_data"]
    SERIALIZED_DATA_FIELD_NUMBER: _ClassVar[int]
    serialized_data: bytes
    def __init__(self, serialized_data: _Optional[bytes] = ...) -> None: ...

class DataRef(_message.Message):
    __slots__ = ["dataref"]
    DATAREF_FIELD_NUMBER: _ClassVar[int]
    dataref: str
    def __init__(self, dataref: _Optional[str] = ...) -> None: ...

class IdTaskArgs(_message.Message):
    __slots__ = ["args", "id", "name"]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    args: bytes
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., args: _Optional[bytes] = ...) -> None: ...

class Status(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: int
    def __init__(self, status: _Optional[int] = ...) -> None: ...

class StatusWithData(_message.Message):
    __slots__ = ["serialized_data", "status"]
    SERIALIZED_DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    serialized_data: bytes
    status: int
    def __init__(self, status: _Optional[int] = ..., serialized_data: _Optional[bytes] = ...) -> None: ...

class TaskNameAndCode(_message.Message):
    __slots__ = ["name", "serialized_task"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SERIALIZED_TASK_FIELD_NUMBER: _ClassVar[int]
    name: str
    serialized_task: bytes
    def __init__(self, name: _Optional[str] = ..., serialized_task: _Optional[bytes] = ...) -> None: ...
