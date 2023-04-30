import { logging, Status } from './util.js';

export const Connection = {
    NONE: 0,
    IPC: 1,
    WS: 2,
    THREAD: 3,
};

export class Worker {
    constructor(idx, connection, connectionType) {
        /*
        Connection should be one of the following:
        - ConnectionType:WS - rayletid
        - ConnectionType:Thread - web worker instance
        */
        this.idx = idx;
        this.locked = false;
        this.connection = connection;
        this.connectionType = connectionType;
    }
  
    lock() {
        this.locked = true;
        logging(`Worker lock: ${this.getId()}`);
    }
  
    unlock() {
        logging(`Worker unlock: ${this.getId()}`);
        this.locked = false;
    }
  
    isLocked() {
        return this.locked;
    }
  
    getId() {
        return this.idx;
    }
  
    getConnectionType() {
        return this.connectionType;
    }
  }

export class Scheduler {
    constructor() {
        this._workerList = [];
        this._id2worker = {};
        this.workerNum = 0;
        this.rr = 0;
        this.tasks = {};
    }
  
    saveTask(task_name, serialized_task, module_list) {
        this.tasks[task_name] = [serialized_task, module_list];
    }
  
    getAllTasks() {
        return this.tasks;
    }
  
    addWorker(connection, connectionType) {
        /*
        Add and connect worker
        Either IPC (grpc) or WebsocketId (in case of different node)
        */
        const worker_id = this.workerNum.toString();
        const worker = new Worker(worker_id, connection, connectionType);
        this._workerList.push(worker);
        this.workerNum += 1;
        this._id2worker[worker_id] = worker;
        return worker;
    }
  
    addWorkerWithId(worker_id, connection, connectionType) {
        /*
        Add and connect worker with Id
        Use this API when Id is assigned from the main raylet.
        Either IPC (grpc) or WebsocketId (in case of different node)
        */
        worker_id = worker_id.toString();
        const worker = new Worker(worker_id, connection, connectionType);
        this.workerNum += 1;
        this._workerList.push(worker);
        this._id2worker[worker_id] = worker;
        return worker;
    }
  
    getAllWorkers() {
        return this._workerList;
    }
  
    getAllLocalWorkers() {
        return this._workerList.filter(worker => worker.getConnectionType() === Connection.THREAD);
    }
  
    acquireWorker() {
        /*
        Acquire the free worker to perform task.
        The worker will be locked.
        */
        // Round-robin
        for (let i = 0; i < this.workerNum; i++) {
            const acq_id = this.rr % this.workerNum;
            const cur_worker = this._workerList[acq_id];
            this.rr += 1;
            if (!cur_worker.isLocked()) {
                cur_worker.lock();
                return cur_worker;
            }
        }
        return null;
    }
  
    freeWorker(worker_id) {
        const worker = this.getWorkerById(worker_id);
        worker.unlock();
    }
  
    getWorkerById(worker_id) {
        return this._id2worker[worker_id] || null;
    }
  }

class VolpyData {
    constructor(ref, loc = null, val = null, fut = null) {
        this.ref = ref;
        this.loc = loc;
        this.val = val;
        this.fut = fut;
        this.status = val ? 0 : -1;
        this.done = !(fut || loc);
    }
  }

export class Datastore {
    constructor() {
        this.dict = {};
    }
  
    get(ref) {
        if (!(ref in this.dict)) {
            return [ Status.DATA_NOT_FOUND, null ];
        }
        const obj = this.dict[ref];
        if (obj.val !== null) {
            return [ obj.status, obj.val ];
        }
        return [ Status.DATA_ON_OTHER, obj.loc ];
    }
  
    put(ref, val) {
        const obj = new VolpyData(ref, null, val);
        this.dict[ref] = obj;
    }
  
    putLoc(ref, loc) {
        const obj = new VolpyData(ref, loc);
        this.dict[ref] = obj;
    }
  
    putFuture(ref, fut) {
        const obj = new VolpyData(ref, null, null, fut);
        this.dict[ref] = obj;
    }
  
    isDone(ref) {
        return this.dict[ref].done;
    }
  
    getFuture(ref) {
        const obj = this.dict[ref];
        if (obj.done) {
            return null;
        }
        return obj.fut;
    }
  
    saveVal(ref, val, status = 0) {
        const obj = this.dict[ref];
        obj.val = val;
        obj.status = status;
        obj.done = true;
    }
}

async function initTask(worker, task_name, serialized_task, module_list) {
    /*
    * Blocking, waiting for the other side to finish initializing task
    */
    if (worker.getConnectionType() === Connection.THREAD) {
        return await worker.connection.initTask(task_name, serialized_task, module_list);
    } else {
        // There shouldn't be any initTask send to worker via this method
        // initTask should be broadcasted through rayletws instead of iterating each worker.
        throw new Error('initTask should be broadcasted through rayletws');
    }
}

async function runTaskLocal(raylet_ws, datastore, worker, cid, ref, task_name, args) {
    /*
     * Run the task and do all routines when the task is finished.
     * 1. Save value into datastore
     * 2. Call FreeWorker to main raylet
     */
    if (worker.getConnectionType() != Connection.THREAD) {
        throw new Error(`Incorrect connectionType: ${worker.getConnectionType()}`);
    }
    const response = await worker.connection.runTask(cid, task_name, args);
    const msg = { "cid": cid, "worker_id": worker.idx };
    datastore.saveVal(ref, response.serialized_data, response.status);
    // Send to main!! Not to the worker conn.
    await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.FreeWorker, msg);
    logging(`Task done: ${cid}`);
    return response;
}
  
async function runTaskRemote(raylet_ws, worker, cid, task_name, args) {
    /*
     * UNLIKE runTaskLocal, we call the remote then we wait for the response status
     * to ensure that the task is started, dataref is saved and broadcasted.
     */
    if (worker.getConnectionType() != Connection.WS) {
        throw new Error(`Incorrect connectionType: ${worker.getConnectionType()}`);
    }
    const msg = { "cid": cid, "worker_id": worker.idx, "task_name": task_name, "args": args };
    const response = await raylet_ws.send(worker.connection.rayletid, raylet_ws.API.WorkerRun, msg);
    return response;
}

export const SharedLogic = {
    initTask, runTaskLocal, runTaskRemote
}