import glob
import os
import sys

def mv_log_files(scenario_path,A=None,B=None,C=None,D=None,E=None,F=None,G=None,H=None,I=None,J=None,debug=False,check_dir=False):

    try:
        if(os.path.isabs(scenario_path)==False):
            scenario_path=os.path.abspath(os.path.normcase(scenario_path))
    except:
        print('[Error] I can\'t find scenario file at LogUtil.py')
        sys.exit(1)

    fp=open(scenario_path,'r')
    scenario_dir=os.path.dirname(scenario_path)
    while True:
        line=fp.readline()
        if not line:
            break
        try:
            option,value=(line.strip()).split('	')
            if option == 'log':
                move_path=log(scenario_dir+'/'+value,A,B,C,D,E,F,G,H,I,J,debug,check_dir)
                if(check_dir):
                    return move_path

        except ValueError:
            print('[Error [{}] format of scenario is like OPTION VALUE'.format(option))
    fp.close()

def log(path,A,B,C,D,E,F,G,H,I,J,debug=False,check_dir=False):
    fp=open(path,'r')
    while True:
        line=fp.readline().strip()
        if not line:
            break
        if line[0]=='#':
            continue

        #ex)~/example/	~/log_monitor/logs/clExample_-A_-B_-C
        find_path, move_path=line.split('	')
        if(A != None):
            move_path=move_path.replace('-A',str(A))
        if(B != None):
            move_path=move_path.replace('-B',str(B))
        if(C != None):
            move_path=move_path.replace('-C',str(C))
        if(D != None):
            move_path=move_path.replace('-D',str(D))
        if(E != None):
            move_path=move_path.replace('-E',str(E))
        if(F != None):
            move_path=move_path.replace('-F',str(F))
        if(G != None):
            move_path=move_path.replace('-G',str(G))
        if(H != None):
            move_path=move_path.replace('-H',str(H))
        if(I != None):
            move_path=move_path.replace('-I',str(I))
        if(J != None):
            move_path=move_path.replace('-J',str(J))
        if(check_dir==True):
            return move_path
        if(os.path.exists(move_path)==False):
            os.system('mkdir -p '+move_path)
        if(debug):
            print('[Log Path] '+move_path)
        if(debug):
            print('[Find file] '+str(glob.glob(find_path+'*.log*')))
            print('How many in there? '+str(len(glob.glob(find_path+'*.log*'))))
        if(len(glob.glob(find_path+'/*.log*'))==0):
            continue
        clear_log_files(glob.glob(find_path+'*.log*'),move_path,debug)
    fp.close()
    if(debug):
        print('[Find file] '+str(glob.glob(os.getcwd()+'/*.log*')))
    clear_log_files(glob.glob(os.getcwd()+'/*.log*'),move_path,debug)

def clear_log_files(log_file,log_dir,debug=False):
    if log_file == None:
        print('[Error] There isn\'t log files')
        return
    for f in log_file:
        if(debug):
            print('[Found Log file] '+f)
        mv_file(f,log_dir,debug)

def mv_file(now_file,mv_path,debug=False):
    if(os.path.exists(mv_path+os.path.basename(now_file))==True):
        for i in range(1,100000):
            if(os.path.exists(mv_path+os.path.basename(now_file+str(i)))==False):
                mv_file=os.path.basename(now_file+str(i))
                if(debug):
                    print('[Move log file] '+mv_file+' to '+ mv_path+mv_file)
                os.system('mv '+now_file+' '+mv_path+mv_file)
                break
                    
    else:
        os.system('mv '+now_file+' '+mv_path)
        if(debug):
            print('mv '+now_file+' '+mv_path)



def merge_into_one(others, target, debug):
    for other in others:
        merge_into(other, target, debug)


def merge_into(src, dst, debug):
    if debug:
        print("[Info] {:s} is merged into {:s}".format(src, dst))
    os.system("cat {:s} >> {:s}".format(src, dst))


