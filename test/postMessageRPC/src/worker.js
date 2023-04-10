import { expose } from 'postmsg-rpc';

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

expose('add', (data) => {
  console.log(data);
  let ret = data.a + data.b;
  console.log(`Here is the result: ${ret}`);
  return ret;
}, opts);