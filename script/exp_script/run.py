#!/usr/bin/env python3

import argparse
import subprocess
import glob
import os
import threading
import time
import signal

from ExprParser import ExprParser
from AppRunner import AppRunner
from LogUtil import clear_log_files
import shlex
def run_apps(app_schedules,cpu_check,debug):
    now = time.time()
    for app_schedule in app_schedules:
        print('app_schedule: ',end='')
        print(app_schedule)
    app_runners = []
    for app_schedule in app_schedules:
        # init cmd doesn't require schedule
        schedule = app_schedule
        app_runners.append(AppRunner(schedule,
                                    now,
                                    debug=debug))
    if(cpu_check):
        #Execute CpuUtilizaiotn
        cpu_cmd=shlex.split(os.getcwd()+'/tools/getCpuUtil.py')
        cpu_thread = subprocess.Popen(cpu_cmd,stdout=subprocess.PIPE,universal_newlines=True)

    #Run Scheduled Experiment
    for i,app_runner in enumerate(app_runners):
        app_runner.start()

    for i,app_runner in enumerate(app_runners):
        return_app=app_runner.join()



    if(cpu_check):
        #Kill CpuUtilization
        if(cpu_thread.poll()==None):
            cpu_thread.send_signal(signal.SIGINT)
        try:
            out, err=cpu_thread.communicate()
        except(subprocess.SubprocessError):
            print('[INFO] CPU Check Error! '+err)
        if(debug):
            print('[INFO] Cpu Utilization Check End!')

        
    if(debug):
        print('[INFO] Execute End')

    return app_runners

def run_expr(expr_schedule,scenario,cpu_check,debug=False):

    # run experiment apps
    run_apps(expr_schedule,cpu_check,debug)


if __name__ == "__main__":
    scenario= ExprParser()
    
    expr_schedule = scenario.expr_schedule
    debug=scenario.debug
    cpu_check=scenario.cpu_check

    run_expr(expr_schedule,scenario,cpu_check,debug)