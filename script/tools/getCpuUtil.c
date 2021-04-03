#include <stdio.h>
#include <stdlib.h>

FILE* fp_top=NULL;
double getCpuUtil(){
	char buf[BUFSIZ]={0x0,};
	if((fp_top=popen("top -b -n1 | grep -Po '[0-9.]+ id' | awk '{print 100-$1}'","r"))==NULL){
		printf("[Error] Can't read cpu Utilization\n");
		exit(1);
	}
	while(fgets(buf,sizeof(BUFSIZ),fp_top)!=NULL){
		if((buf[0]<='9'&&buf[0]>='0')){
			fclose(fp_top);
			return atof(buf);
		}
	}
}

int main(void){
    double cpu=getCpuUtil();
    printf("%f\n",cpu);

    return 0;

}