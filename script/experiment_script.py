#!/usr/bin/env python3
import os
import time
import glob
import argparse
import sys
import subprocess
import signal
import shlex
from exp_script.LogUtil import mv_log_files
from exp_script.written_file import read_file

def checker(dirs):
    if(os.path.exists(dirs)):
        return True
    else:
        return False


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('-scenario',help='Where is scenario file?')
    parser.add_argument('-A',help='app args 1',default=None)
    parser.add_argument('-B',help='app args 2',default=None)
    parser.add_argument('-C',help='app args 3',default=None)
    parser.add_argument('-D',help='app args 4',default=None)
    parser.add_argument('-E',help='app args 5',default=None)
    parser.add_argument('-F',help='app args 6',default=None)
    parser.add_argument('-G',help='app args 7',default=None)
    parser.add_argument('-H',help='app args 8',default=None)
    parser.add_argument('-I',help='app args 9',default=None)
    parser.add_argument('-J',help='app args 10',default=None)

    args=parser.parse_args()
    if len(sys.argv) < 3:
        print('Usage: experiment_script.py -scenario [scenario_file] [-A [args1]] [-B [args2]] [-C [args3]] ...[-I [args10]]\n\n\
ex) experiment_script.py -scenario ./scenario/cpu_intensive1/scenario -A 16 -B 32\n\
expr_schedule 에서 -A -B Argument를 줄 것이다. \n\
ex) expr_schedule\n\
../bin/clExample -A -B --> clExample 16 32 를 실행한다.\n')
        exit(1)

    scenario_path=args.scenario
    A = args.A==None if None else args.A
    B = args.B==None if None else args.B
    C = args.C==None if None else args.C
    D = args.D==None if None else args.D
    E = args.E==None if None else args.E
    F = args.F==None if None else args.F
    G = args.G==None if None else args.G
    H = args.H==None if None else args.H
    I = args.I==None if None else args.I
    J = args.J==None if None else args.J
    debug=False
    cpu_util_check_using_shell=True #Cpu Utilization을 측정하는 것
    gpu_util_check=True #Gpu Utilization을 측정하는 것
    shared=True #shared memory는 libclsched.so 에게 [subkernel size]와 [device]를 선택케 하는 공유메모리. libclsched.so를 쓰지 않으면 안켜도된다.

    # scenario 1
    SUBKERNEL_X=[16,32,64,128,256,512,1024,2048,4096,5000]                                    
    FILTER=[7]
    # scenario 2
    #SUBKERNEL_X=4000                                                   
    #SUBKERNEL_Y=[16,32,64,128,256,512,1024,2048,4000]                                    
    # Square
    #SUBKERNEL=[16,32,64,128,256,512,1024]
    DEVICE=0
    
    for s_x in SUBKERNEL_X:
        s_y=s_x
        if(s_x==5000):
            s_y=6000
        # If you want to check up Log file
        check_dir=mv_log_files(scenario_path,s_x,s_y,C,D,E,F,G,H,I,J,debug,True)
        if(checker(check_dir)):
            print(check_dir+' is already done!')
            continue
        
        if(shared==True):
            #Usage: shared_memory <subkernel_x> <subkernel_y> <device>
            shared_cmd=shlex.split(os.getcwd()+'/tools/shared_memory {} {} {}'.format(s_x,s_y,DEVICE))
            shared_memory=subprocess.Popen(shared_cmd,stdout=subprocess.PIPE,universal_newlines=True)
            if(shared_memory.poll()!=None):
                print('[Error] Shared memory isn\'t open!')
                exit(1)
                    
        if(gpu_util_check==True):
            getGpuUtil_cmd=shlex.split(os.getcwd()+'/tools/getGpuUtil')
            getGpuUtil=subprocess.Popen(getGpuUtil_cmd,stdout=subprocess.PIPE,universal_newlines=True)
            if(getGpuUtil.poll()!=None):
                print('[Error] Shared memory isn\'t open!')
                exit(1)

        #scenario파일을 읽고 App에  바꿔 줄 args1, args2 전달
        #Usage: experiment_script.py -scenario [scenario_path] -A [arg1] -B [arg2] -C [arg3] -D [arg4]
        #ex: experiment_script.py -scenario ./scenario/cpu_intensive1/scenario -A 32 -B 1024 -C 256 -D 0
        read_file(scenario_path,s_x,s_y,C,D,E,F,G,H,I,J,debug)

        #log 한번 지워주고
        try:
            os.system('rm '+os.getcwd()+'/*.log*')
        except:
            pass
        proc_cmd=shlex.split('./exp_script/run.py -scenario {} -debug {} -cpu {}'.format(scenario_path,debug,cpu_util_check_using_shell))
        proc=subprocess.Popen(proc_cmd,stdout=subprocess.PIPE,universal_newlines=True)
        out,err=proc.communicate()
        if(debug):
            print(out)
        if(err!=None):
            print(err)
        
        #로그 파일을 참고하여 로그파일 만든다.
        #cpu_intensive1_log
        #~/example/	~/log_monitor/logs/ffmpeg_clExample_-A_-B_-C/
        # *.log ----> ffmpeg_clExample_-A_-B_-C
        mv_log_files(scenario_path,s_x,s_y,C,D,E,F,G,H,I,J,debug)

        if(gpu_util_check==True):
            getGpuUtil.send_signal(signal.SIGKILL)
            out,err=getGpuUtil.communicate()
            if(debug):
                print(out)
            if(err!=None):
                print(err)
            os.system('pkill -9 -ef getGpuUtil')

        if(shared==True):
            shared_memory.send_signal(signal.SIGKILL)
            out,err=shared_memory.communicate()
            if(debug):
                print(out)
            if(err!=None):
                print(err)
            ipc_kill_cmd=shlex.split(os.getcwd()+'/tools/kill_ipc.sh')
            shmid=subprocess.Popen(ipc_kill_cmd,stdout=subprocess.PIPE,universal_newlines=True)
            out,err=shmid.communicate()
            if(debug):
                print(out)
            if(err!=None):
                print(err)
        
        time.sleep(1)