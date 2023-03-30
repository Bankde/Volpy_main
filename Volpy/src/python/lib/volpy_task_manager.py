import codepickle
import cloudpickle
from .singleton import Singleton
import asyncio
from .util import counter, Status

# We don't use import singleton ipc_caller here because 
# this module could be in either REPL or workers.

class VolpyDataRef(object):
    ipc_caller = None

    def __init__(self, ref:str):
        self.ref = ref

    @classmethod
    def setup(cls, ipc_caller):
        cls.ipc_caller = ipc_caller

    def get(self):
        '''
        Get the result from the task.
        This method is synchronous and will block until the execution is finished.
        '''
        task = self.ipc_caller.Get(self.ref)
        loop = asyncio.get_running_loop()
        response = loop.run_until_complete(task)
        if response.status == 0:
            return task_manager.deserializeData(response.serialized_data)
        else:
            raise RuntimeError(response.status)

class TaskManager(object, metaclass=Singleton):
    def setup(self, ipc_caller):
        self.ipc_caller = ipc_caller
        VolpyDataRef.setup(self.ipc_caller)
        codepickle.set_config_get_import(True)

    def _generateRemoteFunc(self, func):
        def remote(*kwargs) -> VolpyDataRef:
            serialized_data = self.serializeData(kwargs)
            cid = counter.getCount()
            loop = asyncio.get_running_loop()
            # Blocking won't take long because raylet will generate and send ref back to us
            response = loop.run_until_complete(self.ipc_caller.SubmitTask(cid, func.__name__, serialized_data))
            status, ref = response.status, response.dataref
            if status != Status.SUCCESS:
                raise Exception(f"Error creating task: {status}")
            dataRef = VolpyDataRef(ref)
            return dataRef
        return remote

    def registerRemote(self, func):
        serializedTask, module_list = self.serializeUploadTask(func)
        taskname = func.__name__
        loop = asyncio.get_running_loop()
        loop.run_until_complete(self.ipc_caller.CreateTask(taskname, serializedTask, module_list))
        func.remote = self._generateRemoteFunc(func)

    def serializeData(self, args):
        return cloudpickle.dumps(args)

    def deserializeData(self ,args):
        return cloudpickle.loads(args)

    def serializeUploadTask(self, task):
        return codepickle.dumps(task)

    def deserializeUploadTask(self, serializedTask):
        task = codepickle.loads(serializedTask)
        task.remote = self._generateRemoteFunc(task)
        return task

    def put(self, data):
        serialized_data = self.serializeData(data)
        loop = asyncio.get_running_loop()
        response = loop.run_until_complete(self.ipc_caller.Put(serialized_data))
        status, ref = response.status, response.dataref
        dataRef = VolpyDataRef(ref)
        return dataRef

task_manager = TaskManager()
registerRemote = task_manager.registerRemote
serializeUploadTask = task_manager.serializeUploadTask
deserializeUploadTask = task_manager.deserializeUploadTask
put = task_manager.put