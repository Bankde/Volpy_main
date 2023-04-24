import { SimpleWS } from './simple_ws.js';
import { Status, logging, generateDataRef } from './util.js';
import { SharedLogic, Connection } from './raylet_scheduler';

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
        NOP: 0,
        CreateTask: 1,
        GetAllTasks: 2,

        InitWorker: 11,
        AcquireWorker: 12,
        FreeWorker: 13,
        WorkerRun: 14,

        SaveDataRef: 21,
        GetData: 22
    }

    addHandler() {
        // {"task_name": str, "serialized_task": bytes}
        // ret: {"status": int}
        this.setCallback(VolpyWS.API.CreateTask, async (data) => {
            return await this.createTask(data);
        });
        // {"cid": int, "worker_id": str, "task_name": str, "args": bytes}
        // ret: {"status": int, "dataref": str}
        // A command to run the task on this node. Behave like running task with ipc.
        // Will broadcast dataref to other nodes with its rayletid.
        // Return dataref, the result data of the task will store locally.
        this.setCallback(VolpyWS.API.WorkerRun, async (data) => {
            return await this.workerRun(data);
        });
        // {"dataref": str, "rayletid": str}
        // ret: {"status": int}
        // Tell raylet that the pair of dataRef and its location
        this.setCallback(VolpyWS.API.SaveDataRef, async (data) => {
            return await this.saveDataRef(data);
        });
        // {"dataref": str}
        // ret: {"status": int, "serialized_data": bytes}
        // Get data from ref
        this.setCallback(VolpyWS.API.GetData, async (data) => {
            return await this.getData(data);
        });
    }

    addDataCallback() {
        const targetData = ["serialized_task", "serialized_data", "args"];
        this.dataRecvCallback = ((data) => {
            if (data == null) {
                return data
            }
            for (const key of targetData) {
                if (key in data) {
                    let raw_data = atob(data[key]);
                    let dataArr = new Uint8Array(raw_data.length);
                    for (let i=0; i<raw_data.length; i++) {
                        dataArr[i] = raw_data.charCodeAt(i);
                    }
                    data[key] = dataArr;
                }
            }
            return data
        });
        this.dataSendCallback = ((data) => {
            if (data == null) {
                return data
            }
            for (const key of targetData) {
                if (key in data) {
                    let s = [];
                    let raw_data = data[key];
                    for (let i=0; i<raw_data.length; i++) {
                        s.push(String.fromCharCode(raw_data[i]));
                    }
                    let b64_data = btoa(s.join(''));
                    data[key] = b64_data;
                }
            }
            return data
        });
    }

    async createTask(data) {
        /*
        Receive CreateTask from raylet (either main/not) ws.
        As browser node, declare the task in each worker thread.
        */
        let { task_name, serialized_task, module_list } = data;
        logging(`Recv CreateTask: ${task_name}`);
        this.scheduler.saveTask(task_name, serialized_task, module_list);
        let workers = this.scheduler.getAllLocalWorkers();
        // Broadcast to all worker thread
        let tasks = [];
        workers.forEach((worker) => {
            let task = SharedLogic.initTask(worker, task_name, serialized_task, module_list);
            tasks.push(task);
        });
        let responses = await Promise.all(tasks);
        let msg_obj = { "status": Status.SUCCESS };
        return msg_obj
    }

    async workerRun(data) {
        let { cid, worker_id, task_name, args } = data;
        logging(`Recv workerRun: ${cid} ${worker_id} ${task_name}`);
        // TODO: ADD (don't forget to change dataref)
        let worker = this.scheduler.getWorkerById(worker_id);
        // There shouldn't be a workerRun call that will redirect us back to remote ws
        if (worker.getConnectionType() != Connection.THREAD) {
            throw new Error(`Incorrect connectionType: ${worker.getConnectionType()}`);
        }
        let ref = generateDataRef();
        logging(`Generate ref: ${cid} ${ref}`);
        let task = SharedLogic.runTaskLocal(this, this.datastore, worker, cid, ref, task_name, args);
        this.datastore.putFuture(ref, task);
        // Broadcast to all raylet that we own the data
        let msg = { "dataref": ref, "rayletid": this.getId() };
        let response = await this.broadcast(this.API.SaveDataRef, msg);
        let msg_obj = { "status": Status.SUCCESS, "dataref": ref };
        return msg_obj
    }

    async saveDataRef(data) {
        let { dataref, rayletid } = data;
        this.datastore.putLoc(dataref, rayletid);
        let msg_obj = { "status": Status.SUCCESS };
        return msg_obj;
    }

    async getData(data) {
        let { dataref } = data;
        // unlike IPC case, when we get ws request, it should guarantee that the data is here.
        let fut = this.datastore.getFuture(dataref);
        if (fut != null) {
            let response = await fut;
            this.datastore.saveVal(dataref, response.serialized_data, response.status);
        }
        let [ status, val ] = this.datastore.get(dataref);
        logging(`Get: ${status} ${val}`);
        let msg_obj = {"status": status, "serialized_data": val}
        return msg_obj
    }
}

export function VolpyWSCreateSession(config) {
    let session = new VolpyWS(config);
    session.init(config.uuid);
    session.addHandler();
    session.addDataCallback();
    session.start();
    return session;
}