#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import signal
import shlex

path=os.getcwd()+'/cpuUtilization.log'
cpu_cmd=('top -b -n1 | grep -Po \'[0-9.]+ id\' | awk \'{print 100-$1}\'')
def handler(signum,f):
    fp.close()
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT,handler)
    fp=open(path,'a+')
    while(True):
        try:
            cpuUtil=subprocess.check_output(cpu_cmd,shell=True,universal_newlines=True)
            fp.write(str(time.time())+','+cpuUtil)
        except(subprocess.CalledProcessError):
            fp.close()
    
