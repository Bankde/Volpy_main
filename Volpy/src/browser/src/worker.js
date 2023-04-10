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
