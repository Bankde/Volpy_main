const { logging } = require('./util.js');

class Worker {
    constructor(idx, connection) {
        this.idx = idx;
        this.locked = false;
        this.connection = connection;
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
        return this.connection.getConnectionType();
    }
  }

class Scheduler {
    constructor() {
        this._workerList = [];
        this._id2worker = {};
        this.workerNum = 0;
        this.rr = 0;
        this.tasks = {};
    }
  
    saveTask(taskname, serialized_task) {
        this.tasks[taskname] = serialized_task;
    }
  
    getAllTasks() {
        return this.tasks;
    }
  
    addWorker(connection) {
        /*
        Add and connect worker
        Either IPC (grpc) or WebsocketId (in case of different node)
        */
        const worker_id = this.workerNum.toString();
        const worker = new Worker(worker_id, connection);
        this._workerList.push(worker);
        this.workerNum += 1;
        this._id2worker[worker_id] = worker;
        return worker;
    }
  
    addWorkerWithId(worker_id, connection) {
        /*
        Add and connect worker with Id
        Use this API when Id is assigned from the main raylet.
        Either IPC (grpc) or WebsocketId (in case of different node)
        */
        worker_id = worker_id.toString();
        const worker = new Worker(worker_id, connection);
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

class Datastore {
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
        const obj = new this.VolpyData(ref, null, val);
        this.dict[ref] = obj;
    }
  
    putLoc(ref, loc) {
        const obj = new this.VolpyData(ref, loc);
        this.dict[ref] = obj;
    }
  
    putFuture(ref, fut) {
        const obj = new this.VolpyData(ref, null, null, fut);
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
  

module.exports = {
    Worker,
    Scheduler,
    Datastore
}