const { VolpyWSCreateSession } = require('./raylet_ws');
const { UUIDGeneratorBrowser } = require('./util');
import { VolpyWorker } from './worker_mgr.js';
const { Scheduler, Datastore } = require('./raylet_scheduler');

document.addEventListener('DOMContentLoaded', function() {
    // Update recommend workerNum from hardware
    const cpuCount = navigator.hardwareConcurrency;
    document.getElementById("cpuCountRecommend").innerHTML = `(Rec: ${cpuCount})`;
    document.getElementById("workerNum").value = cpuCount;
    // Update button
    const button = document.getElementById("runNodeBtn");
    button.addEventListener('click', runNode);
});

function runNode() {
    let wssAddr = document.getElementById("wssAddr").value;
    let realm = document.getElementById("wssRealm").value;
    let workerNum = document.getElementById("workerNum").value;
    console.log(wssAddr + " " + workerNum);

    let config = {
        url: wssAddr,
        realm: realm
    }
    config.uuid = UUIDGeneratorBrowser();
    console.log("Current NodeID: " + config.uuid);

    const session = VolpyWSCreateSession(config);
    const scheduler = new Scheduler();
    const datastore = new Datastore();

    let workers = [];
    for (let i=0; i<workerNum; i++) {
        let worker = new VolpyWorker();
        workers.push(worker);
    }
}