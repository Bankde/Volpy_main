from .volpy_task_manager import task_manager

tasklist = {}

class ExecutionError(Exception):
    pass

class SerializationError(Exception):
    pass

def initTask(task_name, serialized_task):
    tasklist[task_name] = task_manager.deserializeUploadTask(serialized_task)

def executeTask(task_name, serialized_data):
    try:
        kwargs = task_manager.deserializeData(serialized_data)
        ret = tasklist[task_name](*kwargs)
    except:
        raise ExecutionError
    try:
        serialized_data = task_manager.serializeData(ret)
    except:
        raise SerializationError
    return serialized_data