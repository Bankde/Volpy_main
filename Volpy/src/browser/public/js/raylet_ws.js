import { SimpleWS } from './simple_ws.js';
import { Status, logging } from './util.js';

export class VolpyWS extends SimpleWS {
    constructor(config) {
        super(config)
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
        this.setCallback(this.API.CreateTask, this.createTask)
        // {"cid": int, "worker_id": str, "task_name": str, "args": bytes}
        // ret: {"status": int, "dataref": str}
        // A command to run the task on this node. Behave like running task with ipc.
        // Will broadcast dataref to other nodes with its rayletid.
        // Return dataref, the result data of the task will store locally.
        this.setCallback(this.API.WorkerRun, this.workerRun)
        // {"dataref": str, "rayletid": str}
        // ret: {"status": int}
        // Tell raylet that the pair of dataRef and its location
        this.setCallback(this.API.SaveDataRef, this.saveDataRef)
        // {"dataref": str}
        // ret: {"status": int, "serialized_data": bytes}
        // Get data from ref
        this.setCallback(this.API.GetData, this.getData)
    }

    async createTask(data) {
        /*
        Receive CreateTask from raylet (either main/not) ws.
        As browser node, declare the task in each worker thread.
        */
       let { task_name, serialized_task } = data;
       logging(`Recv CreateTask: ${task_name}`);
        // TODO: ADD

        msg_obj = {"status": Status.SUCCESS};
        return msg_obj
    }

    async workerRun(data) {
        let { cid, worker_id, task_name, args } = data;
        logging(`Recv workerRun: ${cid} ${worker_id} ${task_name}`);
        // TODO: ADD (don't forget to change dataref)

        msg_obj = {"status": Status.SUCCESS, "dataref": "1"};
        return msg_obj
    }
      
}