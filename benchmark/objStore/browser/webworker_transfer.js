// webworker.js

importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js");

let get_N_index = null;

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide();
  get_N_index = await self.pyodide.runPythonAsync(`
  def get_N_index(arr, ind):
      return arr[ind]
  get_N_index
  `);
}
let pyodideReadyPromise = loadPyodideAndPackages();
const script = `ret = get_N_index(data, ind)`;

self.onmessage = async (event) => {
  // make sure loading is done
  await pyodideReadyPromise;
  // Now is the easy part, the one that is similar to working in the main thread:
  const {id, data, ind} = event.data;
  try {
    let result = get_N_index(data, ind);
    self.postMessage({id, result, data}, [data.buffer]); // transfer data back
  } catch (error) {
    console.log(id, error.message);
  }
};