import { caller, expose } from 'postmsg-rpc';
import { logging, Status } from './util';
importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.1/full/pyodide.js");
// import { loadPyodide } from 'pyodide'; // This one doesn't work for webworker.

// Don't worry about race condition during the initial script runs.
// https://html.spec.whatwg.org/multipage/workers.html#worker-processing-model

const opts = {
    addListener: (m, h) => {
        addEventListener(m, h);
    },
    removeListener: (m, h) => {
        removeEventListener(m, h);
    },
    postMessage: (t, a) => {
        postMessage(t); /* For worker: Only msg, drop origin. */
    }
};

self.Status = Status;
self.createTaskStub = caller('CreateTask', opts);
self.submitTaskStub = caller('SubmitTask', opts);
// getAllTaskStrub = caller('GetAllTasks', opts); // Shouldn't be used unless we introduce worker killing/reset.
self.getStub = caller('Get', opts);
self.putStub = caller('Put', opts);

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage("micropip");
    self.micropip = pyodide.pyimport("micropip");
    await self.micropip.install(["numpy", "cloudpickle"]);
    await self.micropip.install("/static/codepickle-2.2.0.dev0-py3-none-any.whl")
    await self.pyodide.runPythonAsync(`
from js import Status, createTaskStub, submitTaskStub, getStub, putStub
import codepickle
import cloudpickle
import sys, inspect, pyodide
print("Current Python " + str(sys.version))

### TaskManager

counter = 0
def getCount():
    global counter
    counter += 1
    return counter

# codepickle.set_config_get_import(True)

class VolpyDataRef(object):
    ipc_caller = None

    def __init__(self, ref:str):
        self.ref = ref

    def get(self):
        '''
        Get the result from the task.
        This method is synchronous and will block until the execution is finished.
        '''
        msg = { "dataref": self.ref }
        task = getStub(msg)
        loop = asyncio.get_running_loop()
        response = loop.run_until_complete(task)
        if response.status == 0:
            return task_manager.deserializeData(response.serialized_data)
        else:
            raise RuntimeError(response.status)

def _generateRemoteFunc(func):
    def remote(*kwargs) -> VolpyDataRef:
        serialized_data = serializeData(kwargs)
        cid = getCount()
        loop = asyncio.get_running_loop()
        # Blocking won't take long because raylet will generate and send ref back to us
        response = loop.run_until_complete(self.ipc_caller.SubmitTask(cid, func.__name__, serialized_data))
        status, ref = response.status, response.dataref
        if status != Status.SUCCESS:
            raise Exception(f"Error creating task: {status}")
        dataRef = VolpyDataRef(ref)
        return dataRef
    return remote

def registerRemote(func):
    serializedTask, module_list = serializeUploadTask(func)
    taskname = func.__name__
    loop = asyncio.get_running_loop()
    loop.run_until_complete(self.ipc_caller.CreateTask(taskname, serializedTask, module_list))
    func.remote = _generateRemoteFunc(func)

def serializeData(args):
    return cloudpickle.dumps(args)

def deserializeData(args):
    return cloudpickle.loads(args)

def serializeUploadTask(task):
    return codepickle.dumps(task)

def deserializeUploadTask(serializedTask):
    task = codepickle.loads(serializedTask)
    task.remote = _generateRemoteFunc(task)
    return task

def put(data):
    serialized_data = serializeData(data)
    loop = asyncio.get_running_loop()
    response = loop.run_until_complete(self.ipc_caller.Put(serialized_data))
    status, ref = response.status, response.dataref
    dataRef = VolpyDataRef(ref)
    return dataRef

### Executor

tasklist = {}

def initTask(task_name, p_serialized_task):
    serialized_task = p_serialized_task.to_py()
    tasklist[task_name] = deserializeUploadTask(serialized_task)

async def executeTask(task_name, p_serialized_data):
    try:
        serialized_data = p_serialized_data.to_py()
        kwargs = deserializeData(serialized_data)
        task = tasklist[task_name]
        if inspect.iscoroutinefunction(task):
            ret = await task(*kwargs)
        else:
            # TODO: try asyncio.to_thread
            ret = task(*kwargs)
    except:
        return [Status.EXECUTION_ERROR, b""]
    try:
        serialized_data = serializeData(ret)
    except:
        return [Status.SERIALIZATION_ERROR, b""]
    js_serialized_data = pyodide.ffi.to_js(serialized_data)
    return [Status.SUCCESS, js_serialized_data]
    `);
}
let pyodideReadyPromise = loadPyodideAndPackages();

// const py_initTask = pyodide.globals.get("initTask");
// const executeTask = pyodide.globals.get("executeTask");

expose('InitTask', async (data) => {
    await pyodideReadyPromise;
    const py_initTask = pyodide.globals.get("initTask");
    let { task_name, serialized_task, module_list } = data;
    logging(`Recv InitTask: ${task_name}`);
    await self.micropip.install(module_list);
    await py_initTask(task_name, serialized_task);
    return 0;
}, opts);

expose('RunTask', async (data) => {
    await pyodideReadyPromise;
    const py_executeTask = pyodide.globals.get("executeTask");
    let { cid, task_name, args } = data;
    logging(`Recv RunTask: ${cid} ${task_name}`);
    let ret = (await py_executeTask(task_name, args)).toJs({depth:1});
    let status = ret[0];
    let serialized_data = ret[1];
    let msg = { "status": status, "serialized_data": serialized_data};
    return msg;
}, opts);

// call initWorker after finishing everything.
(caller('InitWorker', opts))();