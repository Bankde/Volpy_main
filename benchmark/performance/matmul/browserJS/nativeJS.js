function matmul(A, B, C, size) {
	for (let i=0; i<size; i++) {
		for (let j=0; j<size; j++) {
			let sum = 0;
			for (let k=0; k<size; k++) {
				sum += A[i*size + k] * B[k*size + j];
			}
			C[i*size + j] = sum;
		}
	}
}

function genMat(size) {
	let buffer = new ArrayBuffer(size*size*4);
	let ret = new Int32Array(buffer);
	for (let i=0; i<size*size; i++) {
		ret[i] = (Math.round(Math.random() * 20) - 10);
	}
	return ret;
}

var size = 125;
console.log("Testing size: " + size);
let data = [];
for (let i=0; i<100; i++) {
	let A = genMat(size);
	let B = genMat(size);
	let C = new Int32Array(size*size);
	let start = new Date().getTime();
	matmul(A, B, C, size);
	let end = new Date().getTime();
	console.log("Time: " + (end-start));
	data.push((end-start));
}
document.getElementsByTagName('body')[0].innerHTML = data.toString();
document.title = "Done";