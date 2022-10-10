#include <iostream>
#include <sys/time.h>
#include <fstream>
using namespace std;

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
	ofstream resultFile;
	resultFile.open("result.txt");
	for (int i=0; i<100; i++) {
		long start = getMsTime();
		double ret = giga_flop();
		long end = getMsTime();
		// cout << "Ans: " << ret << std::endl;
		cout << "Time: " << (end - start) << endl;
		resultFile << (end - start) << endl;
	}
	resultFile.close();
	return 0;
}
