import codepickle
import cloudpickle
from .singleton import Singleton
import asyncio
from .util import counter, Status
import volpy # Abstraction for VolpyDataRef.__reduce__

# We don't use import singleton ipc_caller here because 
# this module could be in either REPL or workers.

class VolpyDataRef(object):
    ipc_caller = None

    def __init__(self, ref:str):
        self.ref = ref

    @classmethod
    def setup(cls, ipc_caller):
        cls.ipc_caller = ipc_caller

    async def get(self):
        '''
        Get the result from the task.
        '''
        response = await self.ipc_caller.Get(self.ref)
        if response.status == 0:
            return task_manager.deserializeData(response.serialized_data)
        else:
            raise RuntimeError(response.status)
        
    def __reduce_ex__(self, __protocol):
        return (volpy.VolpyDataRef, (self.ref,))
    
    def __repr__(self):
        return str(self.ref)

class TaskManager(object, metaclass=Singleton):
    def setup(self, ipc_caller):
        self.ipc_caller = ipc_caller
        VolpyDataRef.setup(self.ipc_caller)
        codepickle.set_config_get_import(True)

    def _generateRemoteFunc(self, func):
        async def remote(*kwargs) -> VolpyDataRef:
            serialized_data = self.serializeData(kwargs)
            cid = counter.getCount()
            # Blocking won't take long because raylet will generate and send ref back to us
            response = await self.ipc_caller.SubmitTask(cid, func.__name__, serialized_data)
            status, ref = response.status, response.dataref
            if status != Status.SUCCESS:
                raise Exception(f"Error creating task: {status}")
            dataRef = VolpyDataRef(ref)
            return dataRef
        return remote

    async def registerRemote(self, func):
        serializedTask, module_list = self.serializeUploadTask(func)
        taskname = func.__name__
        await self.ipc_caller.CreateTask(taskname, serializedTask, module_list)
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
    
    async def get(self, dataref):
        if isinstance(dataref, VolpyDataRef):
            return await dataref.get()
        elif isinstance(dataref, str):
            return await VolpyDataRef(dataref).get()
        else:
            raise RuntimeError(f'Incorrect type for dataref: got {type(dataref)}, expected str or VolpyDataRef')

    async def put(self, data):
        serialized_data = self.serializeData(data)
        response = await self.ipc_caller.Put(serialized_data)
        status, ref = response.status, response.dataref
        dataRef = VolpyDataRef(ref)
        return dataRef

task_manager = TaskManager()
registerRemote = task_manager.registerRemote
serializeUploadTask = task_manager.serializeUploadTask
deserializeUploadTask = task_manager.deserializeUploadTask
put = task_manager.put
get = task_manager.get