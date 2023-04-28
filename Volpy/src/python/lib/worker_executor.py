from .volpy_task_manager import task_manager
import inspect
import logging, traceback

tasklist = {}

class ExecutionError(Exception):
    pass

class SerializationError(Exception):
    pass

def initTask(task_name, serialized_task, module_list=None):
    tasklist[task_name] = task_manager.deserializeUploadTask(serialized_task)

async def executeTask(task_name, serialized_data):
    try:
        kwargs = task_manager.deserializeData(serialized_data)
    except:
        raise SerializationError
    try:
        task = tasklist[task_name]
        if inspect.iscoroutinefunction(task):
            ret = await task(*kwargs)
        else:
            # TODO: try asyncio.to_thread? so our execution doesn't block the ipc.
            ret = task(*kwargs)
    except Exception as e:
        err_msg = traceback.format_exc()
        logging.info(err_msg) # So programmer knows what's wrong.
        raise ExecutionError
    try:
        serialized_data = task_manager.serializeData(ret)
    except:
        raise SerializationError
    return serialized_data