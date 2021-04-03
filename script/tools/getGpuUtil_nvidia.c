#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(){
	FILE* fp=NULL;
	char line[BUFSIZ];

	/* 명령어 수행에 대한 pipe를 호출함 */
	if((fp=popen("nvidia-smi --format=csv --query-gpu=utilization.gpu","r"))==NULL)
		return 1;
	
	/* ls -al 명령어로 출력하는 내용을 한줄씩 읽어서 처리 함*/
	int cnt=0;
	while(fgets(line,BUFSIZ,fp)!=NULL){
		cnt++;
		if(cnt==2){
			printf("%d\n",atoi(line));
			cnt=0;
		}
	}
	pclose(fp);
	return 0;
}