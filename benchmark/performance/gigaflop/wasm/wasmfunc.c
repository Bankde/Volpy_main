double giga_flop() {
	double x = 3.14159;
	int i;
	for (i=0; i<500000000; i++) {
		x += 5.12313123;
		x *= 0.5398394834;
	}
	return x;
}
