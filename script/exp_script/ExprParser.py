import argparse
import os
import time
import sys

def ExprParser():
    parser = argparse.ArgumentParser()

    #-log_dir [log_dir's name]
    parser.add_argument("-scenario", help='Where is scenario file?')
    parser.add_argument("-debug", help='Where is scenario file?',default=False)
    parser.add_argument("-cpu", help='Do you wan\'t to check cpu util?',default=False)

    args = parser.parse_args()
    scenario_path=args.scenario
    debug=args.debug
    cpu_check=args.cpu

    try:
        if(os.path.isabs(scenario_path)==False):
            scenario_path=os.path.abspath(os.path.normcase(scenario_path))
    except:
        print('[Error] I can\'t find scenario file at written_file.py')
        sys.exit(1)
    if(debug):
        print('[scenario_path] '+scenario_path)
    return test_case(scenario_path,debug,cpu_check)

class test_case:
    def __init__(self,scenario_path,debug,cpu_check):
        self.scenario_path=scenario_path
        self.debug=debug
        self.data=self.read_file()
        self.expr_schedule=self.data.get('expr_schedule')
        if(cpu_check=='True'):
            self.cpu_check=True
        else:
            self.cpu_check=False


    def read_file(self):
        f=open(self.scenario_path,'r')
        scenario_dir=os.path.dirname(self.scenario_path)
        return_dict={}
        while True:
            line=f.readline()
            if not line:
                break
            try:
                option, value =(line.strip()).split('	')
                if option == 'expr_schedule':
                    if(self.debug):
                        print('[expr_schedule file in run.py] '+scenario_dir+'/'+value+'_exp')
                    return_dict['expr_schedule']=self.schedule(scenario_dir+'/'+value+'_exp')

            except ValueError:
                print("[Error] [{}] format of scenario is like OPTION  VALUE".format(option))
                sys.exit(1)
     
        f.close()

        return return_dict 


        
    def parseLog(self,app_list):
        ###debug
        #self.logdir: _[WG]_[SUB]_[GLOBAL] ex) _1_1_1
        #app_list: ['/home/root/nfs/gpgpu/example/clmatmul/bin/clExample 1 1', ' ...' ]
        #now_app: ['clExample','....']

        log_roc={}
        #log_roc['App']='original log location'
        #ex) loc_roc['clExample']=os.getcwd()+'/../../gpgpu/example/clmatmul/*.log'
        is_log_dir=False
        for app in app_list:
            now_app=app.split('/')[-1].split()[0]
            if(now_app.find('ffmpeg')==-1):
                log_roc[now_app]=os.getcwd()+'/*.log'
                ## <-- now_app의 original 로그가 저장된 위치 입력. original log는 self.savefolder_CL 로 나중에 옮겨질 것이다.
                #ffmpeg은 거의 항상 돌아가기 때문에 common log dir name으로 하기 적절치 않다.
                if(is_log_dir==False):
                    self.logdir=now_app+self.logdir
                    is_log_dir=True
            if(now_app.find('ffmpeg')!=-1):
                log_roc[now_app]=os.getcwd()+'/ffmpeg*.log'
                #ffmpeg의 log는 현재 폴더에 생성된다.

        #debug
        #self.logdir=clExample_1_1_1
        self.savefolder=os.getcwd()+'/../log_monitor/logs/'+self.logdir+'/'
        #self.savefolder=now/../log_monitor/logs/clExample_1_1_1/
        self.savefolder_CL=self.savefolder+'CL/'
        #self.savefolder_CL=now/../log_monitor/logs/clExample_1_1_1/CL/
        self.savefolder_ffmpeg=self.savefolder+'ffmpeg/'
        #self.savefolder_ffmpeg=now/../log_monitor/logs/clExample_1_1_1/ffmpeg/

        if(os.path.exists(self.savefolder)==False):
            os.system('mkdir -p '+self.savefolder)
            os.system('mkdir -p '+self.savefolder_CL)
            os.system('mkdir -p '+self.savefolder_ffmpeg)
        if(self.debug==True):
            print("[INFO] Your log file will be save at :"+self.savefolder)
        #print(log_roc)
        #{'clExample': '/home/pllpokko/workspace/experiment/matmul_experiment/opencl-lg19/script/../../gpgpu/example/clmatmul/*.log'}
        return log_roc
        

    def schedule(self,path):
        if(self.debug):
            print('[Read schedule in schedule, ExprParser.py] '+path)
        f=open(path,'r')
        return_list=[]
        app_dict={}#한 실험에서 한 앱이 몇번 중복 실행하는지 기록함. app_list['clExample']=3
        while True:
            line=f.readline().strip()
            if not line:
                break
            try:
                if(self.debug):
                    print('[Read CMD] ',end='')
                    print((line.strip()).split('	'))
                
                app, start, end, env, app_type= (line.strip()).split('	')
                start=float(start)
                if(end=='inf'):
                    end=float('inf')
                else:
                    end=float(end)

            except ValueError:
                print("[Error] format of expr_schedule is " \
                        "App_START_END_ENV")
                sys.exit(1)
            if (end != float('inf')):
                if start > end:
                    print("[Error] start time can't be bigger than end time")
                    sys.exit(1)
                exec=end-start
            if (end==float('inf')):
                if(self.debug==True):
                    print("[INFO] "+app+"is executed during inf time")
                exec=float('inf')
            env=env.split(';')
            envs=os.environ.copy()
            for env_var in env:
                key,val=env_var.split('=')
                envs[key]=val
            #app_type=((((app.strip()).split(' '))[0]).split('/'))[-1]
            #보통은 app 명령이 ~/my/dir/clExample -arg1 -arg2 이런식이다. 


            if(app_dict.get(app_type)==None):
                #app_dict[app_type]이 기록되어 있지않다면, 즉 처음 실행하는 App이라면, 
                app_dict[app_type]=0
            else:
                how_many=app_dict.get(app_type)
                how_many+=1
                app_dict[app_type]=how_many
            return_list.append([app,start,exec,envs,app_type,app_dict.get(app_type)])
        
        f.close()
        return return_list
            
