import { caller, expose } from 'postmsg-rpc';
import { logging, Status, generateDataRef } from './util';
import { Worker_Connection, Connection } from './raylet_distribute_logic';

// postmsg-rpc uses the ESM export syntax which forces all modules
// that implements it to use ESM export syntax as well. (bruh)

var scheduler = null;
var datastore = null;
var raylet_ws = null;
var raylet_distribute_logic = null;

export class VolpyWorker {
  constructor() {
    // https://lists.whatwg.org/pipermail/help-whatwg.org/2010-August/003219.html
    // It's important to define all the RPCs in sync before the main returns to the event loop.
    this.worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
    let opts = {
      addListener: (m, h) => {
        this.worker.addEventListener(m, h);
      },
      removeListener: (m, h) => {
        this.worker.removeEventListener(m, h);
      },
      postMessage: (t, a) => {
        this.worker.postMessage(t); /* For worker: Only msg, drop origin. */
      }
    };
    this.initTaskStub = caller('InitTask', opts);
    this.runTaskStub = caller('RunTask', opts);

    expose('CreateTask', async (data) => {
      let { task_name, serialized_task, module_list } = data
      logging(`Recv CreateTask: ${task_name}`)
      scheduler.saveTask(task_name, serialized_task, module_list);
      let tasks = [];
      // Broadcast to all raylets through ws
      let msg = { task_name, serialized_task, module_list };
      let task = raylet_ws.broadcast(raylet_ws.API.CreateTask, msg);
      tasks.push(task);
      // Broadcast to all webworker
      let workers = scheduler.getAllLocalWorkers();
      workers.forEach(worker => {
        task = raylet_distribute_logic.initTask(worker, task_name, serialized_task);
        tasks.push(task);
      });
      responses = await Promise.all(tasks);
      return Status.SUCCESS;
    }, opts);

    expose('SubmitTask', async (data) => {
      let { cid, task_name, args } = data;
      logging(`Recv SubmitTask: ${cid} ${task_name}`);
      let msg = { cid, task_name, args };
      let response = await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.AcquireWorker, msg);
      let worker_id = response.worker_id;
      let worker = scheduler.getWorkerById(worker_id);
      if (worker == null) {
        logging(`All worker busy: ${cid}`);
        return { "status": Status.WORKER_BUSY, "dataref": "" };
      }

      let dataref = null;
      logging(`Worker acquire: ${cid} ${worker.getId()}`);
      if (worker.getConnectionType() == Connection.THREAD) {
        dataref = generateDataRef();
        let task = raylet_distribute_logic.runTaskLocal(worker, cid, ref, task_name, args);
        datastore.putFuture(ref, task);
        // Broadcast to all raylet that we own the data
        let msg = { "dataref": dataref, "rayletid": raylet_ws.getId() };
        response = await raylet_ws.broadcast(raylet_ws.API.SaveDataRef, msg);
      } else {
        response = await raylet_distribute_logic.runTaskRemote(worker, cid, task_name, args);
      }
      logging(`Generate ref: ${cid} ${ref}`);
      return { "status": response.status, "dataref": dataref };
    }, opts);

    expose('InitWorker', async (data) => {
      let msg = { "rayletid": raylet_ws.getId() };
      let response = await raylet_ws.send(raylet_ws.getMainId(), raylet_ws.API.InitWorker, msg);
      let { status, worker_id } = response;
      // We use the id desinated from main, however the worker is connected to our local as thread
      // So we still set worker id here; the rayletws will only be set in main raylet.
      let wcon = new Worker_Connection(worker=this);
      let worker = scheduler.addWorkerWithId(worker_id, wcon);
      logging(`Worker connected (side,thread): ${worker.getId()}}`);
      return { "status": Status.SUCCESS };
    }, opts);

    expose('GetAllTasks', async (data) => {
      // All webworker should be initialized at the same time as browser raylet
      // So this API should not be called
      throw new Exception("Impossible flow");
    }, opts);

    expose('Get', async (data) => {
      // This API is blocking until the task is finished and return the result.
      let ref = data.dataref;
      let fut = datastore.getFuture(ref);
      if (fut != null) {
        let response = await fut;
      }
      let [ status, val ] = datastore.get(ref);
      if (status == Status.DATA_ON_OTHER) {
        // Call WS to get data from other raylet then save it locally
        let rayletid = val;
        let msg = { "dataref": ref };
        let response = await raylet_ws.send(rayletid, raylet_ws.API.GetData, msg);
        [ status, val ] = response.status, response.serialized_data;
        datastore.saveVal(ref, val, status);
      }
      return { "status": status, "serialized_data": val };
    }, opts);

    expose('Put', async (data) => {
      let val = data.serialized_data;
      let ref = generateDataRef();
      datastore.put(ref, val);
      // Broadcast dataref to all raylets
      let msg = { "dataref": ref, "rayletid": raylet_ws.getId() };
      let response = await raylet_ws.broadcast(raylet_ws.API.SaveDataRef, msg);
      return { "status": Status.SUCCESS, "dataref": ref };
    }, opts);
  }

  async initTask(task_name, serialized_task, module_list) {
    let data = { task_name, serialized_task, module_list };
    return await this.initTaskStub(data);
  }

  async runTask(cid, task_name, args) {
    let data = { cid, task_name, args };
    return await this.initTaskStub(data);
  }
}