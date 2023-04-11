export const Connection = {
    NONE: 0,
    IPC: 1,
    WS: 2,
    THREAD: 3,
};

let raylet_ws = null;
let IPCCaller = null;
let datastore = null;

export function setup(l_raylet_ws, l_datastore) {
    raylet_ws = l_raylet_ws;
    datastore = l_datastore;
}

export class Worker_Connection {
    constructor(worker = null, rayletid = null) {
        if (worker) {
            this.connectionType = Connection.THREAD;
            this.worker = worker;
        } else if (rayletid) {
            this.connectionType = Connection.WS;
            // No need for this.rayletws, use the singleton instead.
            this.rayletid = rayletid;
        } else {
            throw new Exception("Incorrect connection");
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

    getWorker() {
        return this.worker;
    }
}

export async function initTask(worker, task_name, serialized_task, module_list) {
    /*
    * Blocking, waiting for the other side to finish initializing task
    */
    if (worker.connection.getConnectionType() === Connection.THREAD) {
        return await worker.connection.worker.initTask(task_name, serialized_task, module_list);
    } else {
        // There shouldn't be any initTask send to worker via this method
        // initTask should be broadcasted through rayletws instead of iterating each worker.
        throw new Error('initTask should be broadcasted through rayletws');
    }
}

export async function runTaskLocal(worker, cid, ref, task_name, args) {
    /*
     * Run the task and do all routines when the task is finished.
     * 1. Save value into datastore
     * 2. Call FreeWorker to main raylet
     */
    assert(worker.connection.getConnectionType() == Connection.THREAD);
    const response = await worker.connection.worker.runTask(cid, task_name, args);
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
  
export async function runTaskRemote(worker, cid, task_name, args) {
    /*
     * UNLIKE runTaskLocal, we call the remote then we wait for the response status
     * to ensure that the task is started, dataref is saved and broadcasted.
     */
    assert(worker.connection.getConnectionType() == Connection.WS);
    const msg = { "cid": cid, "worker_id": worker.idx, "task_name": task_name, "args": args };
    const response = await raylet_ws.send(worker.connection.rayletid, raylet_ws.API.WorkerRun, msg);
    return response;
}