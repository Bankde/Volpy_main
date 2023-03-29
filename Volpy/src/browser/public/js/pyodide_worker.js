// webworker.js

importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js");

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage(["numpy"]);
//   await self.pyodide.runPythonAsync(`
// import numpy as np
// STEP = 1000 ** 2
// def pi_monte_carlo(CORE):
//     circle_points = 0
//     square_points = 0
//     for i in range(STEP // CORE):
//         rand_x = np.random.uniform(-1, 1)
//         rand_y = np.random.uniform(-1, 1)
//         origin_dist = rand_x**2 + rand_y**2
//         if origin_dist <= 1:
//             circle_points += 1
//         square_points += 1
//     return (circle_points, square_points)
//     `)
}
let pyodideReadyPromise = loadPyodideAndPackages();

const WorkerAPI = {
    NONE: 0,
    INIT_TASK: 1,
    RUN_TASK: 2,
};

async function initTask(request) {
    let { task_name, serialized_task } = request;
    logging(`Recv InitTask: ${task_name}`);
}

async function runTask(request) {
    let { cid, task_name, args } = request;
    logging(`Recv RunTask: ${cid} ${task_name}`);
}

self.onmessage = async (event) => {
    // make sure loading is done
    await pyodideReadyPromise;
    // Now is the easy part, the one that is similar to working in the main thread:
    let { id, api, request } = event.data;
    switch (api) {
        case WorkerAPI.NONE:
            throw new Error(`Wrong PyodideWorker API: ${api}`);

        case WorkerAPI.INIT_TASK:
            ret = await initTask(request);

        case WorkerAPI.RUN_TASK:
            ret = await runTask(request);
            
        default:
            self.postMessage({id, ret});
    }
};