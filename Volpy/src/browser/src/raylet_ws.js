const { SimpleWS } = require('./simple_ws.js');
const { Status, logging } = require('./util.js');

class VolpyWS extends SimpleWS {
    constructor(config) {
        super(config)
        this.API = VolpyWS.API;
    }

    setup(scheduler, datastore) {
        this.scheduler = scheduler;
        this.datastore = datastore;
    }

    static API = {
        /* Comment are Main Raylet API (unused here) */
        NOP: 0,
        CreateTask: 1,
        // GetAllTasks: 2,

        // InitWorker: 11,
        // AcquireWorker: 12,
        // FreeWorker: 13,
        WorkerRun: 14,

        SaveDataRef: 21,
        GetData: 22
    }

    addHandler() {
        // {"task_name": str, "serialized_task": bytes}
        // ret: {"status": int}
        this.setCallback(VolpyWS.API.CreateTask, this.createTask);
        // {"cid": int, "worker_id": str, "task_name": str, "args": bytes}
        // ret: {"status": int, "dataref": str}
        // A command to run the task on this node. Behave like running task with ipc.
        // Will broadcast dataref to other nodes with its rayletid.
        // Return dataref, the result data of the task will store locally.
        this.setCallback(VolpyWS.API.WorkerRun, this.workerRun);
        // {"dataref": str, "rayletid": str}
        // ret: {"status": int}
        // Tell raylet that the pair of dataRef and its location
        this.setCallback(VolpyWS.API.SaveDataRef, this.saveDataRef);
        // {"dataref": str}
        // ret: {"status": int, "serialized_data": bytes}
        // Get data from ref
        this.setCallback(VolpyWS.API.GetData, this.getData);
    }

    async createTask(data) {
        /*
        Receive CreateTask from raylet (either main/not) ws.
        As browser node, declare the task in each worker thread.
        */
        let { task_name, serialized_task } = data;
        logging(`Recv CreateTask: ${task_name}`);
        // TODO: ADD

        let msg_obj = {"status": Status.SUCCESS};
        return msg_obj
    }

    async workerRun(data) {
        let { cid, worker_id, task_name, args } = data;
        logging(`Recv workerRun: ${cid} ${worker_id} ${task_name}`);
        // TODO: ADD (don't forget to change dataref)

        let msg_obj = {"status": Status.SUCCESS, "dataref": "1"};
        return msg_obj
    }

    async saveDataRef(data) {
        let { dataref, rayletid } = data;
        this.datastore.putLoc(dataref, rayletid);
        let msg_obj = {"status": Status.SUCCESS};
        return msg_obj;
    }

    async getData(data) {
        let { dataref } = data;
        // unlike IPC case, when we get ws request, it should guarantee that the data is here.
        let fut = this.datastore.getFuture(dataref);
        if (fut != None) {
            response = await fut;
            this.datastore.saveVal(dataref, response.serialized_data, response.status);
        }
        let [ status, val ] = this.datastore.get(dataref);
        let msg_obj = {"status": status, "serialized_data": val}
        return msg_obj
    }
}

function VolpyWSCreateSession(config) {
    let session = new VolpyWS(config);
    session.init(config.uuid);
    session.addHandler();
    session.start();
    return session;
}

module.exports = {
    VolpyWS: VolpyWS,
    VolpyWSCreateSession: VolpyWSCreateSession
}