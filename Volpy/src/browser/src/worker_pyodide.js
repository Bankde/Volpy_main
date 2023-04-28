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
const createTaskStub = caller('CreateTask', opts);
const submitTaskStub = caller('SubmitTask', opts);
// getAllTaskStrub = caller('GetAllTasks', opts); // Shouldn't be used unless we introduce worker killing/reset.
const getStub = caller('Get', opts);
const putStub = caller('Put', opts);

self.CreateTask = async (task_name, p_serialized_task, p_module_list) => {
    let serialized_task = p_serialized_task.toJs();
    let module_list = p_module_list.toJs();
    let msg = { task_name, serialized_task, module_list }
    return await createTaskStub(msg);
};

self.SubmitTask = async (cid, task_name, p_args) => {
    let args = p_args.toJs();
    let msg = { cid, task_name, p_args }
    return await submitTaskStub(msg);
};

self.Get = async (dataref) => {
    let msg = { dataref };
    return await getStub(msg);
};

self.Put = async (p_serialized_data) => {
    let serialized_data = p_serialized_data.toJs();
    let msg = { serialized_data };
    return await putStub(msg);
};

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage("micropip");
    self.micropip = pyodide.pyimport("micropip");
    await self.micropip.install(["numpy", "cloudpickle"]);
    await self.micropip.install("/static/codepickle-2.2.0.dev0-py3-none-any.whl")
    await self.micropip.install("/static/volpy-1.0-py3-none-any.whl")
    await self.pyodide.runPythonAsync(`
from js import Status, CreateTask, SubmitTask, Get, Put
import codepickle, cloudpickle
import asyncio
import sys, inspect, pyodide, traceback
print("Current Python " + str(sys.version))

counter = 0
def getCount():
    global counter
    counter += 1
    return counter

codepickle.set_config_get_import(True)

class VolpyDataRef(object):

    def __init__(self, ref:str):
        self.ref = ref

    def get(self):
        '''
        Get the result from the task.
        This method is synchronous and will block until the execution is finished.
        '''
        task = Get(self.ref)
        loop = asyncio.get_running_loop()
        response = loop.run_until_complete(task)
        if response.status == 0:
            return task_manager.deserializeData(response.serialized_data)
        else:
            raise RuntimeError(response.status)

    def __reduce_ex__(self, __protocol):
        return (volpy.VolpyDataRef, (self.ref,))
        
    def __repr__(self):
        return str(self.ref)

def _generateRemoteFunc(func):
    def remote(*kwargs) -> VolpyDataRef:
        serialized_data = serializeData(kwargs)
        cid = getCount()
        loop = asyncio.get_running_loop()
        # Blocking won't take long because raylet will generate and send ref back to us
        response = loop.run_until_complete(SubmitTask(cid, func.__name__, serialized_data))
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
    loop.run_until_complete(CreateTask(taskname, serializedTask, module_list))
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

def get(dataref):
    if isinstance(dataref, VolpyDataRef):
        return dataref.get()
    elif isinstance(dataref, str):
        return VolpyDataRef(dataref).get()
    else:
        raise RuntimeError(f'Incorrect type for dataref: got {type(dataref)}, expected str or VolpyDataRef')

def put(data):
    serialized_data = serializeData(data)
    loop = asyncio.get_running_loop()
    response = loop.run_until_complete(Put(serialized_data))
    status, ref = response.status, response.dataref
    dataRef = VolpyDataRef(ref)
    return dataRef

# Abstraction wrapper (For CreateTask and SubmitTask are done at deserializeUploadTask)
import volpy
# get/put is from this pyodide script, they will call JS-Get/Put later.
dep = type('', (), { 'registerRemote': None, 'get': get, 'put': put, 'VolpyDataRef': VolpyDataRef })
volpy.setup(dep)

### Executor

tasklist = {}

def initTask(task_name, serialized_task):
    tasklist[task_name] = deserializeUploadTask(serialized_task)

async def executeTask(task_name, serialized_data):
    try:
        kwargs = deserializeData(serialized_data)
    except:
        return [Status.SERIALIZATION_ERROR, b""]
    try:
        task = tasklist[task_name]
        if inspect.iscoroutinefunction(task):
            ret = await task(*kwargs)
        else:
            # TODO: try asyncio.to_thread
            ret = task(*kwargs)
    except Exception as e:
        raise
        err_msg = traceback.format_exc()
        print(err_msg) # So programmer knows what's wrong.
        return [Status.EXECUTION_ERROR, b""]
    try:
        serialized_data = serializeData(ret)
    except:
        return [Status.SERIALIZATION_ERROR, b""]
    return [Status.SUCCESS, serialized_data]
    `);
}
let pyodideReadyPromise = loadPyodideAndPackages();

// const py_initTask = pyodide.globals.get("initTask");
// const executeTask = pyodide.globals.get("executeTask");

expose('InitTask', async (data) => {
    const py_initTask = pyodide.globals.get("initTask");
    let { task_name, serialized_task, module_list } = data;
    logging(`Recv InitTask: ${task_name}`);
    let tasks = [];
    module_list.forEach((module) => {
        // Use loop so we can't filter/handle error separately
        if (module !== "volpy") {
            tasks.push(self.micropip.install(module));
        }
    });
    await Promise.all(tasks);
    await self.micropip.install(module_list);
    let p_serialized_task = pyodide.toPy(serialized_task);
    await py_initTask(task_name, p_serialized_task);
    return 0;
}, opts);

expose('RunTask', async (data) => {
    const py_executeTask = pyodide.globals.get("executeTask");
    let { cid, task_name, args } = data;
    logging(`Recv RunTask: ${cid} ${task_name}`);
    let p_args = pyodide.toPy(args);
    let p_ret = await py_executeTask(task_name, p_args)
    let ret = p_ret.toJs();
    let status = ret[0];
    let serialized_data = ret[1];
    let msg = { "status": status, "serialized_data": serialized_data};
    return msg;
}, opts);

pyodideReadyPromise.then((result) => {
    // call initWorker after finishing everything.
    (caller('InitWorker', opts))();
});