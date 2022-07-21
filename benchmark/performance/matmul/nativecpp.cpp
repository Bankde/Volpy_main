#include <iostream>
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>

int* matmul(int* A, int* B, int* C, size_t size) {
    for (int i=0; i<size; i++) {
        for (int j=0; j<size; j++) {
            int sum = 0;
            for (int k=0; k<size; k++) {
                sum += A[i*size + k] * B[k*size + j];
            }
            C[i*size + j] = sum;
        }
    }
}

long getMsTime() {
	struct timeval tp;
	gettimeofday(&tp, NULL);
	return tp.tv_sec * 1000 + tp.tv_usec / 1000;
}

int* genMat(int size) {
    int* ret = new int[size*size];
    srand(time(0));
    for (int i=0; i<size*size; i++) {
        ret[i] = (rand()%21)-10;
    }
    return ret;
}

int main() {
    char * val = getenv("SIZE");
    int size = (val != NULL) ? strtol(val, NULL, 10) : 125;
    std::cout << "Testing size: " << size << std::endl;

    int* A = genMat(size);
    int* B = genMat(size);
    int* C = new int[size*size];

	long start = getMsTime();
	int* ret = matmul(A, B, C, size);
	long end = getMsTime();

	std::cout << "Time: " << (end - start) << std::endl;
	return 0;
}
