import { caller } from 'postmsg-rpc';

const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });

document.addEventListener('DOMContentLoaded', function() {
  const buttons = document.querySelectorAll("input.input");
  buttons.forEach(button => {
    button.addEventListener('change', run);
  });
});

const opts = {
  addListener: (m, h) => {
    worker.addEventListener(m, h);
  },
  removeListener: (m, h) => {
    worker.removeEventListener(m, h);
  },
  postMessage: (t, a) => {
    worker.postMessage(t); /* For worker: Only msg, drop origin. */
  }
};

const addFunc = caller('add', opts);

async function run() {
  let num1 = parseInt(document.getElementById("num1").value);
  let num2 = parseInt(document.getElementById("num2").value);
  console.log("Change detected");
  let result = await addFunc({ a: num1, b: num2 });
  document.getElementById("result").value = result;
}