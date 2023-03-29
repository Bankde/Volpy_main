import { SimpleWS } from './simple_ws.js';
import { UUIDGeneratorBrowser } from './util.js';

document.addEventListener('DOMContentLoaded', function() {
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
    let session = new SimpleWS(config);
    let uuid = UUIDGeneratorBrowser();
    console.log("Current NodeID: " + uuid);
    session.init(uuid);
    session.start();
}