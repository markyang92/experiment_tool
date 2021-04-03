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
    usleep(11000);

    return gpuUtil;
}

int main(){
    signal(SIGKILL,(void*)signalHandler);
    while(true){
        fp_gpu=fopen("gpuUtil.log","a+");
        fprintf(fp_gpu,"%f,%.1Lf\n",get_time(),getGpuUtil());
        fclose(fp_gpu);
    }
    return 0;
}

void signalHandler(int signo){
    fclose(fp_gpu);
    printf("getGpuUtil killed\n");
    exit(0);
}
