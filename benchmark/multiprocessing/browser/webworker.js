// webworker.js

importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js");

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide();
  await self.pyodide.loadPackage(["numpy"]);
  await self.pyodide.runPythonAsync(`
import numpy as np
STEP = 1000 ** 2
def pi_monte_carlo(CORE):
    circle_points = 0
    square_points = 0
    for i in range(STEP // CORE):
        rand_x = np.random.uniform(-1, 1)
        rand_y = np.random.uniform(-1, 1)
        origin_dist = rand_x**2 + rand_y**2
        if origin_dist <= 1:
            circle_points += 1
        square_points += 1
    return (circle_points, square_points)
    `)
}
let pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async (event) => {
  // make sure loading is done
  await pyodideReadyPromise;
  // Now is the easy part, the one that is similar to working in the main thread:
  const {id, script} = event.data;
  try {
    let start = new Date().getTime();
    self.pyodide.runPython(script);
    let end = new Date().getTime();
    let timeTaken = (end - start);
    let ret = pyodide.globals.get('ret').toJs();
    let [circles, squares] = ret;
    self.postMessage({id, timeTaken, circles, squares});
  } catch (error) {
    console.log(id, error.message);
  }
};