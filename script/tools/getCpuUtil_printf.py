#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import signal
import shlex

path=os.getcwd()+'/cpuUtilization.log'
cpu_cmd=('top -b -n1 | grep -Po \'[0-9.]+ id\' | awk \'{print 100-$1}\'')
if __name__ == "__main__":
    while(True):
        cpuUtil=subprocess.check_output(cpu_cmd,shell=True,universal_newlines=True)
        print(cpuUtil)
        time.sleep(1)


    
