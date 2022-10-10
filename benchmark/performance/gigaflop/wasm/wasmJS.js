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

async function testWasm() {
  let importObject = {};
  var instance = await WebAssembly.instantiate(wasmByte, importObject);
  var giga_flop = instance.instance.exports.giga_flop;

  let data = [];
  for (let i=0; i<100; i++) {
    let start = new Date().getTime();
    let ret = giga_flop();
    let end = new Date().getTime();
    // console.log("Ans: " + ret);
    console.log("Time: " + (end-start));
    data.push((end-start));
  }
  document.getElementsByTagName('body')[0].innerHTML = data.toString();
  document.title = "Done";
}

testWasm();
