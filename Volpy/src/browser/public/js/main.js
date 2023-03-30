const { VolpyWSCreateSession } = require('./raylet_ws.js');
const { UUIDGeneratorBrowser } = require('./util.js');

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
    config.uuid = UUIDGeneratorBrowser();
    console.log("Current NodeID: " + config.uuid);
    session = VolpyWSCreateSession(config);
}