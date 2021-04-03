#!/usr/bin/python
# pllpokko@kaist.ac.kr
#====================SET============================#
C_END       = "\033[0m"
C_BOLD      = "\033[1m"
C_RED       = "\033[31m"
#==================================================#
import inspect
import sys
import os
import glob
import pandas as pd
import numpy as np

def DebugPrinter(arg):
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info=inspect.getframeinfo(frame)
    # __FILE__      -> info.filename
    # __FUCNTION__  -> info.function
    # __LINE__      -> info.lineno
    print(C_BOLD+C_RED+'{}'.format(arg)+C_END)
    print(C_BOLD+C_RED+'{} {} {}'.format(info.filename, info.function, info.lineno)+C_END)


class makeCsvUsingParsedFile:
    def __init__(self,path,log_list,streamline,tag):
        self.path=path
        self.tag=tag
        self.log_list=log_list
        self.app_data=[]        # clmatmulHybridclGPU_16_1024_1024.log
        self.gpuUtil=None       # gpuUtil.log
        self.cpuUtil=None       # cpuUtilization.log    
        self.ffmpeg=None          # ffmpeg.log
        self.ffmpeg_fps=None    # ffmpeg fps data
        self.framework=None       # framework_result.log             : Framework에서 decomposer()가 받은 프로파일용 정보
        self.kernel=None          # matmul_kernel_result.log         : OpenCL APP에서 NDRangeKernel() 앞 뒤 start, end 정보 등 App 프로파일용 정보
        self.streamline=None    # streamline_[App Title].log
        self.streamline_mode=streamline
        self.toDataFrame(log_list)
        self.exp_start=0.0
        self.exp_end=0.0
        self.getExpTime()
        self.save_csv={}
        # /* for debug */
        #print(self.framework)
        #print(self.kernel)
        #print(self.streamline)
        #print(self.app_data)
        if(len(self.app_data)!=0):
            print(self.app_data)
            self.app_data=self.sort_merge(self.app_data,'start')
        self.stat_merge()       # Modify Log files
        self.get_statistics()   # Get Statistics 
        

    def toDataFrame(self,log_list):
        for log in log_list:
            fname=os.path.basename(log)
            if(fname.find('gpuUtil.log')!=-1):
                self.gpuUtil=pd.read_csv(log)
            elif(fname.find('ffmpeg.log')!=-1):
                self.ffmpeg=pd.read_csv(log)
            elif(fname.find('cpuUtil')!=-1):
                self.cpuUtil=pd.read_csv(log)
            elif(fname.find('ffmpeg-')!=-1):
                self.ffmpeg_fps=pd.read_csv(log)
            elif(fname.find('framework_result')!=-1): # framework_result.log  : Framework에서 decomposer가 받은 프로파일용 로그 정보
                self.framework=pd.read_csv(log)
            elif(fname.find('kernel_result')!=-1): # matmul_kernel_result.log : kernel을 프로파일 한 로그 정보
                self.kernel=pd.read_csv(log)
            elif(fname.find('streamline')!=-1):    # Processed log file by ARM-STREAMLINE
                self.streamline=pd.read_csv(log)
            else:
                # Other Apps    : clmatmulHybridclGPU_16_16_1024_1024_1024_256_256.log
                #print('\n'+C_BOLD+C_RED+fname+C_END)
                self.app_data.append(pd.read_csv(log))
    
    def getExpTime(self):
        gpu_start=0.0
        gpu_end=0.0
        cpu_start=0.0
        cpu_end=0.0
        if(self.gpuUtil is not None):
            self.gpuUtil=self.gpuUtil.set_index('timestamp')
            self.gpuUtil=self.gpuUtil.sort_index()
            gpu_start=self.gpuUtil.index[0]
            gpu_end=self.gpuUtil.index[-1]
        if(self.cpuUtil is not None):
            self.cpuUtil=self.cpuUtil.set_index('timestamp')
            self.cpuUtil=self.cpuUtil.sort_index()
            cpu_start=self.cpuUtil.index[0]
            cpu_end=self.cpuUtil.index[-1]
        if(gpu_start<=cpu_start):
            self.exp_start=cpu_start
        else:
            self.exp_start=gpu_start

        if(cpu_end<=gpu_end):
            self.exp_end=cpu_end
        else:
            self.exp_end=gpu_end
        
        if(self.ffmpeg_fps is not None):
            self.ffmpeg_fps=self.ffmpeg_fps.set_index('timestamp')
            self.ffmpeg_fps=self.ffmpeg_fps.sort_index()
    
    def sort_merge(self,data,standard):
        for i,temp in enumerate(data):
            if(i==0):
                continue
            data[0]=pd.concat([data[0],data[i]],join='outer',sort=True)
        return data[0].sort_values(by=standard)

    def stat_merge(self):
        #=========각 log 파일 가공=========================#
        # 1. app data 가공  ex) clmatmulHybridclGPU_16_16_1024_1024_1024_256_256.log
        if(len(self.app_data)!=0):
            self.app_data['idx']=np.arange(len(self.app_data))
            self.app_data=self.app_data.set_index('idx')
            cmd=self.app_data.loc[0,'cmd']
            if(cmd.lower().find('convolution')!=-1):
                splited_cmd=cmd.split(' ') # convolution_simple_LG 7
                if(len(splited_cmd)!=-1):
                    self.app_data['filter']=splited_cmd[1]

        # 2. kernel_result 가공    ex) matmul_kernel_result.log
        if(self.kernel is not None):
            # time 구하기 #
            self.kernel['time']=self.kernel['end']-self.kernel['start']

            # KPS 구하기 #
            kps_list=[]
            for i in range(0,len(self.kernel)):
                try:
                    kps_list.append(1/(self.kernel.iloc[i]['end']-self.kernel.iloc[i]['start']))
                except ZeroDivisionError:
                    kps_list.append(0)
            self.kernel['kps']=kps_list
            self.kernel['idx']=np.arange(len(self.kernel))
            self.kernel=self.kernel.set_index('idx')

        # 3. streamline_XX.log  ex)streamline_matmulGEMM1_1024_100.log 
        if(self.streamline is not None):
            self.streamline['idx']=np.arange(len(self.streamline))
            self.streamline=self.streamline.set_index('idx')
            for i in range(0,len(self.streamline)): # Convert time format from %M:%S.%mS to $S.$mS
                if(str(self.streamline.loc[i,'Time']).find(':')!=-1):
                    now_time=str(self.streamline.loc[i,'Time']).split(':')
                    result_time=0.0
                    depth=len(now_time)-1
                    for j in range(0,len(now_time)-1):
                        result_time+=float(now_time[j])*60.0*depth
                        depth-=1
                    result_time+=float(now_time[-1])
                    result_time=round(result_time,4)
                    self.streamline.loc[i,'Time']=result_time


    def get_statistics(self):
        #=============================모든 정보를 statistics에 합친다=====================================#
        # csv에 가공해서 넣을 값은 여기서 edit #
        # 1. self.kernel에서 get AVG KPS --> 하나의 statistics csv로
        if(len(self.app_data)!=0):
            for i in range(0,len(self.app_data)):
                avg_kps=self.kernel[(self.kernel['start']>=self.app_data.iloc[i]['start'])&(self.kernel['end']<=self.app_data.iloc[i]['end'])]['kps'].mean()
                self.app_data.loc[i,'avg_kps']=avg_kps
                if(str(self.app_data.loc[i,'avg_kps'])=='nan'):
                    self.app_data.loc[i,'avg_kps']=0

        # 2. self.kernel에서 get AVG time --> 하나의 statistics csv로
        if(self.kernel is not None):
            kps_sum=self.kernel['kps'].sum()
            self.save_csv['Avg.kps']=round(kps_sum/len(self.kernel),4)
            self.save_csv['Avg.time[sec]']=round(self.kernel['time'].mean(),4)

        # 3. self.framework에서 get Subframework size --> statistics csv로
        if(self.framework is not None):
            self.save_csv['work_dim']=self.framework.loc[0,'work_dim']
            self.save_csv['local_x']=self.framework.loc[0,'local_x']
            self.save_csv['local_y']=self.framework.loc[0,'local_y']
            self.save_csv['local_z']=self.framework.loc[0,'local_z']
            self.save_csv['sub_x']=self.framework.loc[0,'sub_x']
            self.save_csv['sub_y']=self.framework.loc[0,'sub_y']
            self.save_csv['sub_z']=self.framework.loc[0,'sub_z']

        # 4. self.gpuUtil에서 get Avg_Gpu_Util  --> statistics csv로 
        if(self.gpuUtil is not None):
            # gpu util은 커널이 돌아 갈때만 체크 하자.
            kernel_start=self.kernel.iloc[0]['start']
            kernel_end=self.kernel.iloc[-1]['end']
            gpu_util=self.gpuUtil[(self.gpuUtil.index>=kernel_start)&(self.gpuUtil.index<=kernel_end)]['util'].mean()
            if(str(gpu_util)=='nan'):
                self.save_csv['Avg_Gpu_Util']=0.0
            else:
                self.save_csv['Avg_Gpu_Util']=round(gpu_util,2)
            gpu_util_max=self.gpuUtil['util'].max()
            self.save_csv['Peak_Gpu_Util']=gpu_util_max

        # 5. self.streamline 에서 구하고 싶은 값 가공 후 -> statistics csv 로
        if(self.streamline is not None):
            Read_Miss_Ratio=[]
            Read_Hit_Ratio=[]
            Write_Miss_Ratio=[]
            Write_Hit_Ratio=[]
            for i in range(0,len(self.streamline)):
                if(self.streamline_mode=='ge'):
                    if(int(self.streamline.loc[i,'Mali L2 Cache Lookups:Read lookup'])<100):
                        Read_Miss_Ratio.append(np.nan)
                        Read_Hit_Ratio.append(np.nan)
                    else:
                        try:
                            now_Read_Miss_Ratio=int(self.streamline.loc[i,'Mali External Bus Accesses:Read transaction'])/int(self.streamline.loc[i,'Mali L2 Cache Lookups:Read lookup'])
                        except ZeroDivisionError:
                            now_Read_Miss_Ratio=0.0
                        Read_Miss_Ratio.append(round(now_Read_Miss_Ratio*100.0,2))
                        Read_Hit_Ratio.append(round(100-Read_Miss_Ratio[-1],2))
                    
                    if(int(self.streamline.loc[i,'Mali L2 Cache Lookups:Write lookup'])<100):
                        Write_Miss_Ratio.append(np.nan)
                        Write_Hit_Ratio.append(np.nan)
                    else:
                        try:
                            now_Write_Miss_Ratio=int(self.streamline.loc[i,'Mali External Bus Accesses:Write transaction'])/int(self.streamline.loc[i,'Mali L2 Cache Lookups:Write lookup'])
                        except ZeroDivisionError:
                            now_Write_Miss_Ratio=0.0
                        Write_Miss_Ratio.append(round(now_Write_Miss_Ratio*100.0,2))
                        Write_Hit_Ratio.append(round(100-Write_Miss_Ratio[-1],2))

                    

                elif(self.streamline_mode=='ce'):
                    if(int(self.streamline.loc[i,'Mali L2 Cache Reads:L2 read lookups'])<100):
                        Read_Miss_Ratio.append(np.nan)
                        Read_Hit_Ratio.append(np.nan)
                    else:
                        now_Read_Hit_Ratio=int(self.streamline.loc[i,'Mali L2 Cache Reads:L2 read hits'])/int(self.streamline.loc[i,'Mali L2 Cache Reads:L2 read lookups'])
                        Read_Hit_Ratio.append(round(now_Read_Hit_Ratio*100.0,2))
                        Read_Miss_Ratio.append(round(100-Read_Hit_Ratio[-1],2))
                    if(int(self.streamline.loc[i,'Mali L2 Cache Writes:L2 write lookups'])<100):
                        Write_Miss_Ratio.append(np.nan)
                        Write_Hit_Ratio.append(np.nan)
                    else:
                        now_Write_Hit_Ratio=int(self.streamline.loc[i,'Mali L2 Cache Writes:L2 write hits'])/int(self.streamline.loc[i,'Mali L2 Cache Writes:L2 write lookups'])
                        Write_Hit_Ratio.append(round(now_Write_Hit_Ratio*100.0,2))
                        Write_Miss_Ratio.append(round(100-Write_Hit_Ratio[-1],2))
                        

            self.streamline['ReadMissRatio(%)']=Read_Miss_Ratio
            self.streamline['WriteMissRatio(%)']=Write_Miss_Ratio
            self.streamline['ReadHitRatio(%)']=Read_Hit_Ratio
            self.streamline['WriteHitRatio(%)']=Write_Hit_Ratio

            AvgReadHitRatio=0.0
            AvgReadHitRatioCnt=0

            AvgWriteHitRatio=0.0
            AvgWriteHitRatioCnt=0
            for i in range(0,len(self.streamline)):
                if(str(self.streamline.loc[i,'ReadHitRatio(%)'])!='nan'):
                    AvgReadHitRatio+=self.streamline.loc[i,'ReadHitRatio(%)']
                    AvgReadHitRatioCnt+=1
                if(str(self.streamline.loc[i,'WriteHitRatio(%)'])!='nan'):
                    AvgWriteHitRatio+=self.streamline.loc[i,'WriteHitRatio(%)']
                    AvgWriteHitRatioCnt+=1
            try:
                self.save_csv['Avg.ReadHitRatio(%)']=round(AvgReadHitRatio/AvgReadHitRatioCnt,2)
            except ZeroDivisionError:
                self.save_csv['Avg.ReadHitRatio(%)']=0.0
            try:
                self.save_csv['Avg.WriteHitRatio(%)']=round(AvgWriteHitRatio/AvgWriteHitRatioCnt,2)
            except ZeroDivisionError:
                self.save_csv['Avg.WriteHitRatio(%)']=0.0
            
            self.save_csv['Avg.GPU_UTIL']=self.streamline[self.streamline['GPU Vertex-Tiling-Compute:Activity']>1.0]['GPU Vertex-Tiling-Compute:Activity'].mean()
        #=================================#


        #=========Common Colums============#
        self.save_csv['App']=self.tag     # 따로 뭐 저장할 공통 Columns 정보가 있다면 여기다 적기
        #==================================#
        idx=self.path.rfind('logs')
        csv_path=self.path[0:idx]+'statistics'
        if(os.path.exists(csv_path)==False):
            os.system('mkdir -p '+csv_path)

        self.save_csv=pd.DataFrame(self.save_csv,index=[0])
        print(self.save_csv)

        self.save_csv.to_csv(csv_path+'/'+os.path.basename(self.path)+'.csv',sep=',',na_rep=np.nan)
        self.save_csv.to_csv(self.path+'/report.csv',sep=',',na_rep=np.nan)
                


def makeCSV(instance,tag):
    makeCsvUsingParsedFile(instance.processPath,instance.doneList,instance.streamline,tag)


def combineCsv(csvObject):
    if(os.path.exists(csvObject.path)==False):
        DebugPrinter('[ERROR] path {} isn\'t exists')
        exit(1)
    if(os.path.exists(csvObject.resultCsv)):
        os.system('rm '+csvObject.resultCsv)
    csvList=glob.glob(csvObject.path+'/*.csv')
    if(len(csvList)==0):
        DebugPrinter('[Error] There aren\'t any csv files')
        exit(1)
    for i,nowCsv in enumerate(csvList):
        if(i==0):
            os.system('cp {} {}'.format(nowCsv,csvObject.resultCsv))
            continue
        makeResult(nowCsv,csvObject.resultCsv)
        if(i==len(csvList)-1):
            print(C_BOLD+C_RED+'[INFO] Making result.pkl Done!'+C_END)
        

def makeResult(now_csv,result):
    now_csv=pd.read_csv(now_csv)
    try:
        now_csv=now_csv.drop(['Unnamed: 0'],axis='columns')
    except:
        pass
    try:
        now_csv=now_csv.drop(['idx'],axis='columns') 
    except:
        pass
    result_csv=pd.read_csv(result)
    try:
        result_csv=result_csv.drop(['Unnamed: 0'],axis='columns')
    except:
        pass
    result_csv=pd.concat([result_csv,now_csv],join='outer',sort=True)
    try:
        result_csv=result_csv.drop(['idx'],axis='columns')
    except:
        pass
    #=========소팅할 columns는 시나리오마다 다를 것 ===============#
    # 그때 마다 Edit #
    result_csv=result_csv.sort_values(by=['sub_x'])
    result_csv['idx']=np.arange(len(result_csv))
    result_csv=result_csv.set_index('idx')
    print(result_csv)
    result_csv.to_csv(result,sep=',',na_rep=np.nan)

