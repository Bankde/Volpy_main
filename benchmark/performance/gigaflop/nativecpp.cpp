#include <iostream>
#include <sys/time.h>

double giga_flop() {
	double x = 3.14159;
	int i;
	for (i=0; i<500000000; i++) {
		x += 5.12313123;
		x *= 0.5398394834;
	}
	return x;
}

long getMsTime() {
	struct timeval tp;
	gettimeofday(&tp, NULL);
	return tp.tv_sec * 1000 + tp.tv_usec / 1000;
}

int main() {
	long start = getMsTime();
	double ret = giga_flop();
	long end = getMsTime();
	std::cout << "Ans: " << ret << endl;
	std::cout << "Time: " << (end - start) << endl;
	return 0;
}
