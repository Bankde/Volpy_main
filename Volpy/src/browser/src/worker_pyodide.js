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
const getAllTasksStub = caller('GetAllTasks', opts);
const getStub = caller('Get', opts);
const putStub = caller('Put', opts);

self.CreateTask = async (task_name, p_serialized_task, p_module_list) => {
    let serialized_task = p_serialized_task.toJs();
    let module_list = p_module_list.toJs();
    let msg = { task_name, serialized_task, module_list }
    let js_res = await createTaskStub(msg);
    return pyodide.toPy(js_res);
};

self.SubmitTask = async (cid, task_name, p_args) => {
    let args = p_args.toJs();
    let msg = { cid, task_name, args }
    let js_res = await submitTaskStub(msg);
    return pyodide.toPy(js_res);
};

self.Get = async (dataref) => {
    let msg = { dataref };
    let js_res = await getStub(msg);
    return pyodide.toPy(js_res);
};

self.Put = async (p_serialized_data) => {
    let serialized_data = p_serialized_data.toJs();
    let msg = { serialized_data };
    let js_res = await putStub(msg);
    return pyodide.toPy(js_res);
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

    async def get(self):
        '''
        Get the result from the task.
        This method is synchronous and will block until the execution is finished.
        '''
        response = await Get(self.ref)
        if response["status"] == 0:
            return deserializeData(response["serialized_data"])
        else:
            raise RuntimeError(response["status"])

    def __reduce_ex__(self, __protocol):
        return (volpy.VolpyDataRef, (self.ref,))
        
    def __repr__(self):
        return str(self.ref)

def _generateRemoteFunc(func):
    async def remote(*kwargs) -> VolpyDataRef:
        serialized_data = serializeData(kwargs)
        cid = getCount()
        response = await SubmitTask(cid, func.__name__, serialized_data)
        status, ref = response["status"], response["dataref"]
        if status != Status.SUCCESS:
            raise Exception(f"Error creating task: {status}")
        dataRef = VolpyDataRef(ref)
        return dataRef
    return remote

async def registerRemote(func):
    serializedTask, module_list = serializeUploadTask(func)
    taskname = func.__name__
    await CreateTask(taskname, serializedTask, module_list)
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

async def get(dataref):
    if isinstance(dataref, VolpyDataRef):
        return await dataref.get()
    elif isinstance(dataref, str):
        return await VolpyDataRef(dataref).get()
    else:
        raise RuntimeError(f'Incorrect type for dataref: got {type(dataref)}, expected str or VolpyDataRef')

async def put(data):
    serialized_data = serializeData(data)
    response = await Put(serialized_data)
    status, ref = response["status"], response["dataref"]
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

async function initTask(task_name, serialized_task, module_list) {
    const py_initTask = pyodide.globals.get("initTask");
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
}

expose('InitTask', async (data) => {
    let { task_name, serialized_task, module_list } = data;
    logging(`Recv InitTask: ${task_name}`);
    await initTask(task_name, serialized_task, module_list);
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

pyodideReadyPromise.then(async (result) => {
    let all_tasks = await getAllTasksStub();
    for (let task_name in all_tasks) {
        let [ serialized_task, module_list ] = all_tasks[task_name];
        await initTask(task_name, serialized_task, module_list);
    }
    // call initWorker after finishing everything.
    await (caller('InitWorker', opts))();
});