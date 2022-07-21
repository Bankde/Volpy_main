var wasmB64 = "wasm_b64_here";

function _base64ToArrayBuffer(base64) {
  let binary_string = window.atob(base64);
  let len = binary_string.length;
  let bytes = new Uint8Array(len);
  for (let i=0; i<len; i++) {
    bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
}

var wasmByte = _base64ToArrayBuffer(wasmB64);

function genMat(buffer, start, len) {
	let ret = new Int32Array(buffer, calMemOffset(start), len)
	for (let i=0; i<len; i++) {
		ret[i] = (Math.round(Math.random() * 20) - 10);
	}
	return ret
}

function calMemOffset(mem) {
  return Math.ceil(mem/4)*4;
}

async function testWasm() {
  const size = 125;
  const arrLen = size*size;
  // 3 matrix of size^2 * sizeof(int) plus few free memory
  const memory = new WebAssembly.Memory({
    initial: Math.ceil((size*size*4*3 + 1000) / 64000),
    maximum: Math.ceil((size*size*4*3 + 1000) / 64000)
  });
  let importObject = {
    env: {
      memory: memory
    }
  };

  var instance = await WebAssembly.instantiate(wasmByte, importObject);
  var matmul = instance.instance.exports.matmul;

  console.log("Testing size: " + size);
  let A = genMat(memory.buffer, 0, arrLen);
  let B = genMat(memory.buffer, arrLen*4, arrLen);
  let C = new Int32Array(memory.buffer, calMemOffset(arrLen*2*4), arrLen)
  let start = new Date().getTime();
  matmul(A.byteOffset, B.byteOffset, C.byteOffset, size);
  let end = new Date().getTime();
  console.log("Time: " + (end-start));
}

testWasm();
