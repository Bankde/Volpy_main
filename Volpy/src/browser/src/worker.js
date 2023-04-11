import { caller, expose } from 'postmsg-rpc';
import { logging } from './util';

// Don't worry about race condition during the initial script runs.
// https://html.spec.whatwg.org/multipage/workers.html#worker-processing-model

const opts = {
    addListener: (m, h) => {
        addEventListener(m, h);
    },
    removeListener: (m, h) => {
        removeEventListener(m, h);
    },
    postMessage: (t, a) => {
        postMessage(t); /* For worker: Only msg, drop origin. */
    }
};

expose('InitTask', (data) => {
    let { task_name, serialized_task, module_list } = data;
    logging(`Recv InitTask: ${task_name}`);
    return 0;
}, opts);

expose('RunTask', (data) => {
    let { cid, task_name, args } = data;
    logging(`Recv RunTask: ${cid} ${task_name}`);
    return 0;
}, opts);

const createTaskStub = caller('CreateTask', opts);
const submitTaskStub = caller('SubmitTask', opts);
// getAllTaskStrub = caller('GetAllTasks', opts); // Shouldn't be used unless we introduce worker killing/reset.
const getStub = caller('Get', opts);
const putStub = caller('Put', opts);

// call initWorker after finishing everything.
(caller('InitWorker', opts))();

// importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js");

// async function loadPyodideAndPackages() {
//     self.pyodide = await loadPyodide();
//     await self.pyodide.loadPackage(["numpy"]);
// //   await self.pyodide.runPythonAsync(`
// // import numpy as np
// // STEP = 1000 ** 2
// // def pi_monte_carlo(CORE):
// //     circle_points = 0
// //     square_points = 0
// //     for i in range(STEP // CORE):
// //         rand_x = np.random.uniform(-1, 1)
// //         rand_y = np.random.uniform(-1, 1)
// //         origin_dist = rand_x**2 + rand_y**2
// //         if origin_dist <= 1:
// //             circle_points += 1
// //         square_points += 1
// //     return (circle_points, square_points)
// //     `)
// }
// let pyodideReadyPromise = loadPyodideAndPackages();