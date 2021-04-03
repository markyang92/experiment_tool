#!/usr/bin/python
import argparse
import os
import sys
import glob
import inspect
C_END       = "\033[0m"
C_BOLD      = "\033[1m"
C_RED       = "\033[31m"
C_YELLOW    = "\033[33m"

def DebugPrinter(arg):
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info=inspect.getframeinfo(frame)
    # __FILE__      -> info.filename
    # __FUCNTION__  -> info.function
    # __LINE__      -> info.lineno
    print(C_BOLD+C_RED+'{}'.format(arg)+C_END)
    print(C_BOLD+C_RED+'{} {} {}'.format(info.filename, info.function, info.lineno)+C_END)

class ParseProcess:
    def __init__(self,path,streamline):
        self.path=path
        self.log_list=self.getLogs()
        self.streamline=streamline
        self.processPath=self.getProcessPath()
        self.doneList=[]
        self.pre_processing()

    def getLogs(self):
        log_list=glob.glob(self.path+'/*.log')
        if(len(log_list)==0):
            DebugPrinter('[ERROR] Couldn\'t find any .log files in {} '.format(self.path))
            exit(1)
        
        return log_list

    def getProcessPath(self):
        processPath=self.path+'/'+os.path.basename(self.path)
        try:
            os.system('mkdir -p '+processPath)
        except:
            DebugPrinter('[ERROR] making dir :'+processPath+' filed')
            exit(1)
        return processPath

    def pre_processing(self):
        for f in self.log_list:
            now_file=os.path.basename(f)
            if(os.path.getsize(f)<1): # File exists but, It is empty.
                DebugPrinter('[WARNING] '+now_file+' size is 0 byte')
            if(now_file.find('parsed')!=-1): # Don't push already pre-processed file in log_list
                continue
            if(now_file.find('cpuUtilization.log')!=-1 or now_file.find('gpuUtil.log')!=-1): # cpu나 gpu Util의 log 파일
                self.doneList.append(self.parsing(f,'util'))
            elif(now_file.find('ffmpeg-')!=-1):  # ffmpeg-xxx.log를 전처리하는 파일. fps 정보가 들어가 있음
                self.doneList.append(self.parsing(f,'fps'))
            elif(now_file.lower().find('streamline')!=-1):  # It was made by ARM-Streamline
                if(self.streamline=='no'):
                    continue
                self.doneList.append(self.parsing(f,'streamline'))
            else: # 그외 log 파일들
                self.doneList.append(self.parsing(f,'app'))     # clmatmulHybridclGPU_16_1024, matmul_result.log...

   
    def parsing(self,log_file,target):
        fp=open(log_file,'r')
        fw=open(log_file+'_parsed.csv','w')
        f_parsed=log_file+'_parsed.csv'
        if(target=='util'):
            self.parsing_util(fp,fw)
        elif(target=='fps'):
            self.parsing_fps(fp,fw)
        elif(target=='streamline'):
            self.parsing_streamline(fp,fw)
        elif(target=='app'): # 그외 app 파일 정보. 
            if((os.path.basename(log_file).lower().find('kernel_result')!=-1)):
                # This Log file was made by Original OpenCL Host program that has NDRangekernel() fuction in code.
                # Usually, [EXAMPLE TITLE]_kernel_result.log (e.g., matmul_kernel_result.log, convolution_kernel_result.log)
                types='kernel'
            elif((os.path.basename(log_file).lower().find('framework_result')!=-1)):
                # This Log file was made by HybridCL Framework. It contains some information
                types='framework'
            else:
                # Neither kernel_result nor framework_result
                types='app' 
            self.parsing_app(fp,fw,types)

        fp.close()
        fw.close()
        os.system('mv '+f_parsed+' '+self.processPath)
        return self.processPath+'/'+os.path.basename(f_parsed)
    
    def parsing_streamline(self,fp,fw):
        founded=False
        columns=[]
        while True:
            line=fp.readline()
            if not line:
                break
            if(self.streamline=='ge'):
                if(founded==False and line.find('Index')==0):
                    now_line=line.strip().split(',')
                    columns=now_line[1:]
                    fw.write('Time,'+','.join(columns)+'\n')
                    founded=True
                elif(founded):
                    line=line.replace('%','0')
                    if(line.find('\"')==-1):
                        now_line=line.strip().split(',')
                        fw.write(','.join(now_line)+'\n')
                    else:
                        now_line=line.strip()
                        start=False
                        now=""
                        for i in range(0,len(now_line)):
                            if(start==False and now_line[i]=='\"'):
                                start=True
                                continue
                            if(start==True and (now_line[i]==',' or now_line[i]=='%')):
                                continue
                            if(start==True and now_line[i]=='\"'):
                                start=False
                                continue
                            now+=now_line[i]
                        fw.write(now+'\n')

            elif(self.streamline=='ce'):
                now_line=line.strip().split()
                if(founded==False and line.find('Index')!=-1):
                    columns.append('Time')
                    print('hihi')
                    exit(1)
                    start=False
                    now=""
                    for i in range(2,len(now_line)):
                        if((start==True and now_line[i]=='Mali')):
                            columns.append(now[:-1])
                            now=""
                            start=False
                        if(i==len(now_line)-1):
                            now+=now_line[i]
                            columns.append(now)
                            founded=True
                        if(start==False and now_line[i]=='Mali'):
                            start=True
                            now+=now_line[i]+' '
                            continue
                        if(start==True and now_line[i]!='Mali'):
                            now+=now_line[i]+' '
                    if(len(columns)==0):
                        DebugPrinter('Couldn\'t found Columns')
                        exit(1)
                    fw.write(','.join(columns)+'\n')

                elif(founded):
                    if(now_line[0].find('-')!=-1):
                        continue
                    if(len(now_line)!=0):
                        for i in range(0,len(now_line)):
                            now=""
                            for j in range(0,len(now_line[i])):
                                if(now_line[i][j]==','):
                                    continue
                                now+=now_line[i][j]
                            now_line[i]=now

                        fw.write(','.join(now_line)+'\n')
                               
    
    def parsing_util(self,fp,fw):
        First_open=True
        while True:
            data=fp.readline().strip()
            if not data:
                break
            now_line=data.split(',')
            if First_open:
                fw.write('timestamp,util\n')
                First_open=False
            if(len(now_line)!=2):
                continue
            fw.write(now_line[0]+','+now_line[1]+'\n')

    def parsing_fps(self,fp,fw):
        start_time=None
        while True:
            data=fp.readline().strip()
            wrong_fps=False
            if not data:
                break
            now_line=data.split(' ')
            if(now_line[0].find('timestamp')!=-1):
                now_line=data.strip().split(' ')
                timestamp=float(now_line[0].strip().split('=')[-1])
                if(start_time==None):
                    start_time=timestamp
                    fw.write('timestamp,fps\n')
                fps=''
                for i,val in enumerate(now_line):
                    if(val.find('fps')!=-1):
                        temp=now_line[i].split('=')
                        if(len(temp[-1])!=0):
                            wrong_fps=True
                            break
                        for j in range(i+1,len(now_line)):
                            if(now_line[j]==''):
                                continue
                            fps=now_line[j]
                            break
                        break
                if(wrong_fps):
                    wrong_fps=False
                    continue
                if(float(fps)>=175.0):
                    DebugPrinter('Cut over 175.0 FPS log. You can fix code')
                    #it is wrong fps
                    continue
                fw.write(str(timestamp)+','+str(fps)+'\n')

    def parsing_app(self,fp,fw,types):   # clMatmulHybridclGPU_16_32.log colvolution_1168_5936.log, framework.log, ...kernel.log
        NumLines=0
        framework_columns=False
        while True:
            line=fp.readline().strip()
            if not line:
                break
            NumLines+=1
            if(types=='framework'):
                # == framework_result.log == #
                # 
                # 2,NULL,NULL,128,38 
                # work_dim, Local Size used in HybridCL, SubKernel Size used in HybridCL
                # ========================== #
                if(framework_columns==False):
                    fw.write('work_dim,local_x,local_y,local_z,sub_x,sub_y,sub_z\n')
                    framework_columns=True
                now_line=line.split(',')
                work_dim=int(now_line[0])
                local=[]
                sub=[]
                standard_index=1
                for i in range(0,work_dim):
                    local.append(now_line[standard_index+i])
                standard_index=standard_index+work_dim
                for i in range(0,work_dim):
                    sub.append(now_line[standard_index+i])

                fw.write('{},'.format(work_dim))
                for i in range(0,3):
                    if(i<len(local)):
                        fw.write('{},'.format(local[i]))
                    else:
                        fw.write('NaN,')
                
                for i in range(0,3):
                    if(i<len(sub)):
                        fw.write(sub[i])
                    else:
                        fw.write('NaN')
                    if(i<len(sub)):
                        fw.write(',')
                    else:
                        fw.write('\n')
                        
            elif(types=='kernel'):
                if(line.find('start')!=-1 and NumLines<=1):
                    continue
                elif(NumLines<=1):
                    fw.write('start,end\n')
                now_line=line.split(',')
                fw.write(','.join(now_line[0:2])+'\n')
                
            else: #clMatmulHybridclGPU_16_32.log
                now_line=line.split(',')
                if(now_line[0]!='start'):
                    #cmd 라인 저장
                    #ex) matmulHybridGPU 16 16 1024 1024 1024, convolution_simple_LG 3
                    bin_file=now_line[-1].split('/')[-1]
                    fw.write(','.join(now_line[0:-1])+','+bin_file+'\n')

                elif(now_line[0]=='start'):
                    fw.write(line+'\n')

        if(NumLines<=1):
            if(types=='framework'):
                fw.write('sub_x,sub_y,sub_z\nNaN,NaN,NaN')
            elif(types=='kernel'):
                fw.write('start,end\nNaN,NaN')

class argument:
    def __init__(self):
        self.initParse()

    def initParse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-path",
                            help="Log Dir or File Path Where You Wan\'t",
                            default=None)
        parser.add_argument("-r",help="search recursive",default=None)
        parser.add_argument("-s",help="Select Streamline Mode",default=None)
        parser.add_argument("-g",help="Draw Graph",default=None)
        parser.add_argument("-tag",default=None)

        args=parser.parse_args()
        self.isPathOrTagNone(args.path,args.tag)
        self.recursive=self.getTrueOrFalse(args.r)
        self.graph=self.getTrueOrFalse(args.g)
        self.dirList=self.getDirList(args.path)
        self.tag=args.tag
        self.getStreamline(args.s)
    
    def isPathOrTagNone(self,arg_path,arg_tag):
        if(arg_path is None or arg_tag is None):
            fp=open("./parsingMaker/usage-parser","r")
            while True:
                line=fp.readline()
                if not line:
                    break
                print(line,end='')
            fp.close()
            exit(1)
    
    def getTrueOrFalse(self,arg):
        if(arg is not None and arg.lower()=='y'):
            return True
        return False
    
    def getDirList(self,path):
        print(C_BOLD+C_YELLOW+'[INFO] Received Path: '+path+C_END)
        path=os.path.abspath(path)
        if(os.path.exists(path)==False):
            DebugPrinter('[ERROR] Can\'t find any directory or file')
            exit(-1)

        if(self.recursive):
            path=path+'/*'
            dirList=glob.glob(path)
        else: # If Path just passed only the one file.
            dirList=[path]
        return dirList

    def getStreamline(self,streamArg):
        if(streamArg is not None and streamArg.lower()=='ce'):
            self.streamline='ce'
        elif(streamArg is not None and streamArg.lower()=='ge'):
            self.streamline='ge'
        else:
            self.streamline='no'

class argumentCsv(argument):
    def initParse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-path",
                            help="CSV files or Dir including CSV files",default=None)
        parser.add_argument("-c",help="/*.csv == combine ==> /result.csv",default=None)
        parser.add_argument("-g",help="Draw Graph with specific result.csv",default=None)

        args=parser.parse_args()
        self.isPathNone(args.path)
        self.combine=self.getTrueOrFalse(args.c)
        self.graph=self.getTrueOrFalse(args.g)
        self.path=args.path
        self.resultCsv=self.path+'/result.csv'

    def isPathNone(self,arg):
        if(arg is None):
            fp=open("./csvMaker/usage-csvCombinder","r")
            while True:
                line=fp.readline()
                if not line:
                    break
                if(line.find('**')!=-1):
                    print(C_BOLD+C_RED+line+C_END,end='')
                else:
                    print(line,end='')
            fp.close()
            exit(1)
