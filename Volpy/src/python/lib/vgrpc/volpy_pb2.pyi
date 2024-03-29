from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

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

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class IdTaskArgs(_message.Message):
    __slots__ = ["args", "cid", "task_name"]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    CID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    args: bytes
    cid: int
    task_name: str
    def __init__(self, cid: _Optional[int] = ..., task_name: _Optional[str] = ..., args: _Optional[bytes] = ...) -> None: ...

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

class StatusWithDataRef(_message.Message):
    __slots__ = ["dataref", "status"]
    DATAREF_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    dataref: str
    status: int
    def __init__(self, status: _Optional[int] = ..., dataref: _Optional[str] = ...) -> None: ...

class TaskNameAndData(_message.Message):
    __slots__ = ["module_list", "serialized_task", "task_name"]
    MODULE_LIST_FIELD_NUMBER: _ClassVar[int]
    SERIALIZED_TASK_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    module_list: _containers.RepeatedScalarFieldContainer[str]
    serialized_task: bytes
    task_name: str
    def __init__(self, task_name: _Optional[str] = ..., serialized_task: _Optional[bytes] = ..., module_list: _Optional[_Iterable[str]] = ...) -> None: ...
