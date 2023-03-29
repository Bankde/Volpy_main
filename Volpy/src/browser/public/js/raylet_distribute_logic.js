const Connection = {
    NONE: 0,
    IPC: 1,
    WS: 2,
};

let raylet_ws = null;
let IPCCaller = null;
let datastore = null;

function setup(l_raylet_ws, l_raylet_ipc_caller, l_datastore) {
    raylet_ws = l_raylet_ws;
    IPCCaller = l_raylet_ipc_caller;
    datastore = l_datastore;
}

class Worker_Connection {
    constructor(workeripc = null, rayletid = null) {
        if (workeripc) {
            this.connectionType = Connection.IPC;
            this.workeripc = workeripc;
            this.ipccaller = new IPCCaller();
            this.ipccaller.connect(`localhost:${workeripc}`);
        } else {
            this.connectionType = Connection.WS;
            // No need for this.rayletws, use the singleton instead.
            this.rayletid = rayletid;
        }
    }

    getConnectionType() {
        return this.connectionType;
    }

    getRayletId() {
        return this.rayletid;
    }

    getIPCPort() {
        return this.workeripc;
    }
}

async function initTask(worker, name, serialized_task) {
    /*
    * Blocking, waiting for the other side to finish initializing task
    */
    if (worker.connection.getConnectionType() === Connection.IPC) {
        return await worker.connection.ipccaller.InitTask(name, serialized_task);
    } else {
        // There shouldn't be any initTask send to worker via this method
        // initTask should be broadcasted through rayletws instead of iterating each worker.
        throw new Error('initTask should be broadcasted through rayletws');
    }
}

async function runTaskLocal(worker, cid, ref, name, args) {
    /*
     * Run the task and do all routines when the task is finished.
     * 1. Save value into datastore
     * 2. Call FreeWorker to main raylet
     */
    assert(worker.connection.getConnectionType() == Connection.IPC);
    const response = await worker.connection.ipccaller.RunTask(cid, name, args);
    const msg = { "cid": cid, "worker_id": worker.idx };
    datastore.saveVal(ref, response.serialized_data, response.status);
    if (config.main) {
      worker.unlock();
    } else {
      // Send to main!! Not to the worker conn.
      await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.FreeWorker, msg);
    }
    console.info(`Task done: ${cid}`);
    return response;
}
  
async function runTaskRemote(worker, cid, name, args) {
    /*
     * UNLIKE runTaskLocal, we call the remote then we wait for the response status
     * to ensure that the task is started, dataref is saved and broadcasted.
     */
    assert(worker.connection.getConnectionType() == Connection.WS);
    const msg = { "cid": cid, "worker_id": worker.idx, "task_name": name, "args": args };
    const response = await raylet_ws.send(worker.connection.rayletid, raylet_ws.API.WorkerRun, msg);
    return response;
}