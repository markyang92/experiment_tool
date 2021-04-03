import subprocess
import time
import threading
import shlex
import os

class ExperimentKillError(Exception):
    def __init__(self, cmd):
        self.cmd = cmd
    def __str__(self):
        return "{:s} is killed because experiment is done".format(self.cmd) 

class AppRunner(threading.Thread):
    def __init__(self,
                schedule,
                absolute_time=0,
                debug=False):
        threading.Thread.__init__(self)
        self.proc = None

        self.schedule=schedule

        self.app, self.start_time, self.execution_time, self.env, self.app_type, self.how_many= schedule

        self.app_cmd=shlex.split(self.app)

        self.absolute_time = absolute_time

        self.debug = debug

        self._return=None

        

    def run(self):
        # starts app at designed time
        if self.debug:
            print("[Info] [{:s}] wait till {:f}".format(self.app, self.start_time))
        self.wait_till(self.start_time)

        # execute app
        if self.debug:
            print("[Info] [{:s}] is executed".format(self.app))

        #start_time
        start_time=time.time()
        if(self.how_many==0):
            fp=open(self.app_type+'.log','w')
        else:
            fp=open(self.app_type+'.log'+str(self.how_many),'w')
        fp.write('start,end,cmd\n')
        fp.write(str(start_time)+',')
        fp.close()
        self.proc = subprocess.Popen(self.app_cmd, env=self.env, stdout=subprocess.PIPE)

        # set timeout
        # after given timeout, app will be killed
        #if(self.execution_time != float("inf")):
        self.set_timeout(self.execution_time)
        out, err=self.proc.communicate()
        if(self.debug):
            print(out)
        if(err!=None):
            print(err)
        self._return=self.app_type
            
    def set_timeout(self, timeout):
        try:
            if self.debug:
                print("[Info] [{:s}] has timeout as {:f}".format(self.app, self.execution_time))
            if timeout == 0:
                self.proc.wait(timeout=float("inf"))
            else:
                self.proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            end_time=time.time()
            if(self.how_many==0):
                fp=open(self.app_type+'.log','a+')
            else:
                fp=open(self.app_type+'.log'+str(self.how_many),'a+') 
            fp.write(str(end_time)+','+str(self.app)+'\n')
            fp.close()
            # app is killed after timeout
            self.proc.kill()
            if self.debug:
                print("[Info] [{:s}] is killed according to the schedule".format(self.app))
            
        except ExperimentKillError as eke:
            end_time=time.time()
            if(self.how_many==0):
                fp=open(self.app_type+'.log','a+')
            else:
                fp=open(self.app_type+'.log'+str(self.how_many),'a+') 
            fp.write(str(end_time)+','+str(self.app)+'\n')
            fp.close()
            # app is killed because experiment is done
            self.proc.kill()
            if self.debug:
                print("[Info] [{:s}] is killed after the experiment is done".format(self.app))
            
        else:
            end_time=time.time()
            if(self.how_many==0):
                fp=open(self.app_type+'.log','a+')
            else:
                fp=open(self.app_type+'.log'+str(self.how_many),'a+') 
            fp.write(str(end_time)+','+str(self.app)+'\n')
            fp.close()
            # app is finisehd before timeout
            if self.debug:
                print("[Info] [{:s}] is finished before the experiment is done".format(self.app))

    def kill_by_raise(self):
        if self.is_alive():
            raise ExperimentKillError(self.schedule[0])

    def wait_till(self, t, interval=0.5):
        if t == 0:
            return

        while self.get_elapsed_time() < t:
            time.sleep(interval)

    def get_elapsed_time(self):
        return time.time() - self.absolute_time
    
    def join(self):
        threading.Thread.join(self)
        return self._return
    
