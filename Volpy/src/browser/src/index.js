import { VolpyWSCreateSession } from './raylet_ws';
import { UUIDGeneratorBrowser, logging } from './util';
import { VolpyWorker } from './worker_mgr.js';
import { Scheduler, Datastore } from './raylet_scheduler';

document.addEventListener('DOMContentLoaded', function() {
    // Update wssAddr to the server domain
    document.getElementById("wssAddr").value = "ws://" + window.location.host.split(":")[0] + ":8080/ws";
    // Update recommend workerNum from hardware
    const cpuCount = navigator.hardwareConcurrency;
    document.getElementById("cpuCountRecommend").innerHTML = `(Rec: ${cpuCount})`;
    document.getElementById("workerNum").value = cpuCount;
    // Update button
    const button = document.getElementById("runNodeBtn");
    button.addEventListener('click', runNode);
});

async function runNode() {
    let wssAddr = document.getElementById("wssAddr").value;
    let realm = document.getElementById("wssRealm").value;
    let workerNum = document.getElementById("workerNum").value;
    logging(wssAddr + " " + workerNum);

    let config = {
        url: wssAddr,
        realm: realm
    }
    config.uuid = UUIDGeneratorBrowser();
    logging("Current NodeID: " + config.uuid);

    const session = VolpyWSCreateSession(config);
    const scheduler = new Scheduler();
    const datastore = new Datastore();
    session.setup(scheduler, datastore);

    // Waiting til raylet_ws connected, may improve later.
    await new Promise(r => setTimeout(r, 1000));

    let all_tasks = (await session.send(session.getMainId(), session.API.GetAllTasks, {})).all_tasks;
    scheduler.saveAllTasks(all_tasks);
    let all_worker_meta = (await session.send(session.getMainId(), session.API.GetWorkerMeta, {})).all_workers;
    scheduler.initWithData(all_worker_meta);
    let all_data_meta = (await session.send(session.getMainId(), session.API.GetDataMeta, {})).all_metadata;
    datastore.initWithData(all_data_meta)

    let workers = [];
    for (let i=0; i<workerNum; i++) {
        let worker = new VolpyWorker(session, scheduler, datastore);
        workers.push(worker);
    }

    logging("Setup Browser Raylet finish")
}