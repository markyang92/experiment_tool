scenario
===

scenario/[senario_name]/scenario 파일을 참조한다.

## expr_schedule
* 실험 스케쥴링 파일
```console
[command]\t[start]\t[end]\t[env1;env2..]\t[app information]

반드시 \t (탭)문자로 구분할 것
ex)

/home/root/nfs/experiment_1919/experiment/ffmpeg/ffmpeg	0	75	PATH=$PATH:/home/root/nfs/	ffmpeg
/home/root/nfs/..../bin/clExample 16 256 256 0	35	55	LD_PRELOAD=/home/root/nfs/.../lib/libclsched.so	clmatmul_16_256_256_0
/home/root/nfs/..../example/clmatmul/bin/clExample 16 256 256 0	35	55	foo=bar	clmatmul_16_256_256_0
/home/example/clmatmul/bin/clExample 16 256	35	55	LD_PRELOAD=/home/root/nfs/gpgpu/lib/libclsched.so	clmatmul_16_256_-A_-B     <--Argument로 준 -A arg1 -B arg2 가 대체 될 것이다.
/home/root/nfs/FFmpeg/ffmpeg	35	55	PATH=$PATH:/home/root/nfs/FFmpeg;LD_PRELOAD=/lib/libclsched.so	thumbnail_hybridcl_cpu_-A_-B
```

shared memory의 Argument가 SUBKERNEL, DEVICE이다.
experiment_script.py의 line 61. /shared_memory [SUBKERNEL] [DEVICE]

이 정보가 로그에 필요하기 때문에, line 77에 **read_file(scenario_path,SUBKERNEL,DEVICE,C,D,E,F,G,H,I,J,debug)** 로 args A args B를 SUBKERNEL,DEVICE 정보를 준다.
이 args가 expr_schedule 파일을 참조하여 -A -B 부분에 args를 넣어 줄 것

read_file(scenario_path,**SUBKERNEL**,**DEVICE**,C,D,E,F,G,H,I,J,debug) 와 같이 명시적으로 args를 줬다면 experiment_script.py 를 실행 시, -A -B 등의 옵션으로 Argumnets를 주지 않아도 된다.

### [command]

앱 실행 커맨드를 절대 경로로 줄 것

### [start]\t[end]

앱 실행 및 종료 시간 설정

### [env1;env2...]

앱 실행시 PATH나 LD_PRELOAD 할 환경변수 설정
2개 이상 필요할 경우 ; 문자로 이어 쓸것
ex)
PATH=$PATH:/home/root/nfs/ffmpeg;LD_PRELOAD=/home/root/nfs/gpgpu/lib/libclsched.so

### [app information]

해당 라인의 command가 app information.log 로 명명되어 로그 파일이 만들어짐
```console
../ffmpeg   0   75  PATH=$PATH:/home/ffmpeg ffmpeg              -> ffmpeg.log
../clExample 16 256 256 0   foo=bar clmatmul_16_256_256_0       -> clmatmul_16_256_256_0.log

read_file(scenario_path,SUBKERNEL,DEVICE,C,D,E,F,G,H,I,J,debug)
../clExample 16 256   foo=bar clmatmul_16_256_-A_-B       -> clmatmul_16_256_256_0.log
```


**app information은 app종류에 따라 다음과 같이 명시할 것 (IMPORTANT!)**

* 순수 APP 실행의 경우

FFmpeg Background App: **ffmpeg**

**clmatmulNativeCpu**

**ThumbNativeCpu**
**ThumbOpenclCpu** 
**ThumbOpenclGpu**

* APP에게 WorkGroup, Global, Subkernel, Device 등을 변경한 경우


ex) **clmatmulNativeCpu_16_1024**
ex) **clmatmulNativeCpu_-A_-B**

ex) **clmatmulHybridclCPU_16_1024_-A_-B**
ex) **clmatmulHybridclGPU_16_1024_-A_-B**

ex) **ThumbHybridclCpu_-A_-B**
ex) **ThumbHybridclGpu_-A_-B**


## log

[log file이 만들어 질 수 있는 장소]\t[log들을 이동 시킬 실험 디렉터리]
```console
/home/root/nfs/experiment_1919/matmul/gpgpu/example/	/home/root/nfs/experiment_1919/experiment/opencl-lg19/log_monitor/logs/only_ffmpeg_480p
```

/home/root/nfs/experiment_1919/matmul/gpgpu/example/*.log* --> ~/logs/only_ffmpeg_480p/ 에 저장 할 것이다.
디렉터리가 없다면 실험 스크립트가 자동으로 만들어 줄 것이다.

하지만 보통 ~/experiment/[your experiment title]/opencl-lg19/script/ 에 보통 log 파일들이 만들어 질 것이다. 따라서 오른쪽 로그들을 저장 시킬 실험 디렉터리에 신경을 쓰자.




