function giga_flop() {
	let x = 3.14159;
	let i = 0;
	for (i=0; i<500000000; i++) {
		x += 5.12313123;
		x *= 0.5398394834;
	}
	return x;
}

for (let i=0; i<100; i++) {
	let start = new Date().getTime();
	let ret = giga_flop();
	let end = new Date().getTime();
	// console.log("Ans: " + ret);
	console.log("Time: " + (end-start));
}

document.title = "Done";