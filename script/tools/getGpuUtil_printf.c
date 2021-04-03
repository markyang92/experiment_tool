#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <sys/time.h>
#include <unistd.h>
#include <signal.h>

FILE* fp_gpu=NULL;
void signalHandler(int signo);
double get_time(){
    struct timeval tv;
    gettimeofday(&tv,NULL);
    return (double)tv.tv_sec+(double)1e-6*tv.tv_usec;
}

long double getGpuUtil() {
    long double gpuUtil;

    FILE *fp;

    fp = fopen("/sys/kernel/debug/mali0/gpu_utilization", "r");
    fscanf(fp, "%*s %*s %Lf", &gpuUtil);
    fclose(fp);

    return gpuUtil;
}

int main(){
    signal(SIGINT,(void*)signalHandler);
    while(true){
		printf("%lf\n",getGpuUtil());
        usleep(1000000);
    }
    return 0;
}

void signalHandler(int signo){
    fclose(fp_gpu);
    printf("getGpuUtil killed\n");
    exit(0);
}
