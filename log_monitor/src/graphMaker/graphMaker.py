#!/usr/bin/python
# pllpokko@kaist.ac.kr
C_END     = "\033[0m"
C_BOLD    = "\033[1m"
C_RED    = "\033[31m"
import math
import inspect
import matplotlib
#If you want to execute python code without jupyter, Then use matplotlib.use('Agg')
matplotlib.use('Agg')
from collections import OrderedDict
from matplotlib import font_manager, rc
font_name = font_manager.FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc").get_name()
rc('font', family=font_name)
import os
import pandas as pd
import scipy.interpolate
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
import datetime as dt
import numpy as np
from pandas import DataFrame
from pandas import Series

def graph(path):
    result=pd.read_csv(path+'/report.csv')
    try:
        result=result.drop(['Unnamed: 0'],axis='columns')
    except:
        pass
    finally:
        result['idx']=np.arange(len(result))
        result=result.set_index('idx')
    print(result)
    stream=pd.read_csv(path+'/streamline_parsed.csv',index_col='idx')
    print(stream)

    png_name=os.path.basename(path)
    #===================저장 이름/그래프형태/타이틀 지정=============================#
    save_name=path+'/'+png_name+'.png'
    title='L2 Cache Hit Ratio, Convolution using GlobalMemory(UnOptimization) Global Size: 5000x6000, Local 16x16, Subkernel 1024x1024'
    #===========================================================================#
    colors1 = ['fuchsia','orange','gold','limegreen','blue','darkblue']

    ax1=plt.figure(figsize=(18,7))
    gs=gridspec.GridSpec(nrows=1,ncols=1,bottom=0.15,top=0.92)
    ax1=plt.subplot(gs[0])
    #ax2=ax1.twinx()
    ax1.set_title(title,fontsize=15)
    lines=[]
    labels=[]

    line1=ax1.plot(stream['time'],stream['MaliL2CacheWriteHitRatio'],color=colors1[0],linewidth=2)
    lines.append(line1[0])
    labels.append('L2 Cache Write Hit Ratio')
    line2=ax1.plot(stream['time'],stream['MaliL2CacheReadHitRatio'],color=colors1[1],linewidth=2)
    lines.append(line2[0])
    labels.append('L2 Cache Read Hit Ratio')

    plt.legend(lines,labels,fontsize=12,loc='upper left')


    #======================================글씨============================================#
    '''
    plt.text(x=128,y=70,s='<--Convolution KPS',  color=colors1[0],weight='bold',rotation=0,fontsize=20)
    plt.text(x=16,y=85,s='GPU lUtil(%)-->',  color=colors1[1],weight='bold',rotation=0,fontsize=20)
    plt.text(x=400,y=0.35,s='GUI KPS Local: 4x4',  color=colors[2],weight='bold',rotation=0,fontsize=14)
    plt.text(x=400,y=0.65,s='GUI KPS Local: 8x8',  color=colors[3],weight='bold',rotation=0,fontsize=14)
    '''
    #=====================================================================================#

    x_title='Time'
    #===== X 값에 넣을 어디 숫자? =====#
    #==============================#


    #== origin_x에 덮어 씌울 값은? ==#
    #=============================#
    ax1.set_xlabel(x_title,fontsize=25)
    ax1.set_ylabel('Hit Ratio',fontsize=25)
    #ax2.set_ylabel('AVG. GPU Util(%)',fontsize=25,color=colors1[1])
    #plt.xticks(origin_x,paste_x,fontsize=25)
    ax1.grid(True)

    #===limit=====#
    ax1.set_ylim(0,100)
    #ax2.set_ylim(40,100)
    #=============#



    plt.savefig(save_name)
    plt.close()




def csvGraph(result_csv):
    dir_path=os.path.dirname(result_csv)
    result=pd.read_csv(result_csv,index_col='idx')
    colors1 = ['fuchsia','orange','darkslateblue','limegreen','blue','darkblue']

    # ===== Select Graph Type ===== #
    graph_type=1
    png_name=os.path.basename(result_csv).split('.')[0]+'.png'
    # ============================= #

    if(graph_type==1):
        print(result)
        data1=result
        #===================저장 이름/그래프형태/타이틀 지정=============================#
        save_name=dir_path+'/'+png_name
        title='Matmul Global=4096x128, Local=16x16, GEMM4'
        #===========================================================================#
    
        ax1=plt.figure(figsize=(18,7))
        gs=gridspec.GridSpec(nrows=1,ncols=1,bottom=0.15,top=0.92)
        ax1=plt.subplot(gs[0])
        ax2=ax1.twinx()
        ax1.set_title(title,fontsize=25)
        lines=[]
        labels=[]

        line1=ax1.plot(data1['sub_x'],data1['Avg.kps'],color=colors1[0],linewidth=2,marker='o')
        lines.append(line1[0])
        labels.append('AVG. KPS')

        #line2=ax2.plot(data1['sub_x'],data1['Avg.ReadHitRatio(%)'],color=colors1[1],linewidth=2,marker='o')
        #lines.append(line2[0])
        #labels.append('AVG ReadHitRatio(%)')

        #line3=ax2.plot(data1['sub_x'],data1['Avg.GPU_UTIL'],color=colors1[2],linewidth=2,marker='o')
        #lines.append(line3[0])
        #labels.append('Avg.GPU Util(%)')


        plt.legend(lines,labels,fontsize=12,loc='upper left')


        #======================================글씨============================================#
        '''
        plt.text(x=128,y=70,s='<--Convolution KPS',  color=colors1[0],weight='bold',rotation=0,fontsize=20)
        plt.text(x=16,y=85,s='GPU lUtil(%)-->',  color=colors1[1],weight='bold',rotation=0,fontsize=20)
        plt.text(x=400,y=0.35,s='GUI KPS Local: 4x4',  color=colors[2],weight='bold',rotation=0,fontsize=14)
        plt.text(x=400,y=0.65,s='GUI KPS Local: 8x8',  color=colors[3],weight='bold',rotation=0,fontsize=14)
        '''
        #=====================================================================================#


        x_title='Subkernel Size'
        #===== X 값에 넣을 어디 숫자? =====#
        origin_x=[]
        origin_x=list(data1['sub_x'])
        #==============================#


        #== origin_x에 덮어 씌울 값은? ==#
        paste_x=[] 
        for i in range(0,len(data1)):
            paste_x.append('{}x{}'.format(data1.loc[i,'sub_x'],data1.loc[i,'sub_y']))
            #paste_x.append('{}x{}'.format(data1.loc[i,'sub_x'],'38'))
        #=============================#
        print('Original: ',end='')
        print(origin_x)
        print('Copy: ',end='')
        print(paste_x)
        
        plt.xscale('log')
        ax1.set_xlabel(x_title,fontsize=25)
        ax1.set_ylabel('Avg. KPS',fontsize=25)
        ax2.set_ylabel('Avg. Cache Read Hit Ratio(%)',fontsize=25)
        plt.xticks(origin_x,paste_x,fontsize=25)
        ax1.minorticks_off()
        ax1.grid(True)

        #===limit=====#
        #ax1.set_ylim(0)
        ax2.set_ylim(0,100)
        #=============#

    
        plt.savefig(save_name)
        plt.close()


    elif(graph_type==2):
        g=result[result['App']=='convolution_global']
        l=result[result['App']=='convolution_local']
        l=l.drop([18])
        print(g)
        print(l)
        #===================저장 이름/그래프형태/타이틀 지정=============================#
        save_name=dir_path+'/convolution.png'
        title='Convolution Mat [5000x6000] Global&Local Ver.'
        #===========================================================================#
    
        ax1=plt.figure(figsize=(18,7))
        gs=gridspec.GridSpec(nrows=1,ncols=1,bottom=0.15,top=0.92)
        ax1=plt.subplot(gs[0])
        ax2=ax1.twinx()
        ax1.set_title(title,fontsize=25)
        lines=[]
        labels=[]

        line1=ax1.plot(g['sub_x'],g['Avg.kps'],color=colors1[0],linewidth=2)
        lines.append(line1[0])
        labels.append('Global Ver. KPS')
        line2=ax2.plot(g['sub_x'],g['Avg_Gpu_Util'],color=colors1[1],linewidth=2)
        lines.append(line2[0])
        labels.append('GPU Util(%)')

        line3=ax1.plot(l['sub_x'],l['Avg.kps'],color=colors1[2],linewidth=2)
        lines.append(line3[0])
        labels.append('Local Ver. KPS')
        line4=ax2.plot(l['sub_x'],l['Avg_Gpu_Util'],color=colors1[3],linewidth=2)
        lines.append(line4[0])
        labels.append('GPU Util(%)')

        plt.legend(lines,labels,fontsize=12,loc='upper left')


        #======================================글씨============================================#
        plt.text(x=64,y=20,s='<--Conv Global KPS',  color=colors1[0],weight='bold',rotation=0,fontsize=20)
        '''
        plt.text(x=16,y=20,s='Conv Local KPS-->',  color=colors1[1],weight='bold',rotation=0,fontsize=20)
        '''
        plt.text(x=15,y=20,s='Conv Local KPS-->',  color=colors1[2],weight='bold',rotation=0,fontsize=20)
        '''
        plt.text(x=400,y=0.65,s='GUI KPS Local: 8x8',  color=colors[3],weight='bold',rotation=0,fontsize=14)
        '''
        #=====================================================================================#

        x_title='Subkernel Size'
        #===== X 값에 넣을 어디 숫자? =====#
        origin_x=[]
        origin_x=list(g['sub_x'])
        #==============================#


        #== origin_x에 덮어 씌울 값은? ==#
        paste_x=[] 
        for i,now_x in enumerate(origin_x):
            if(i==len(origin_x)-1):
                paste_x.append('{}x{}'.format(now_x,6000))
            else:
                paste_x.append('{}x{}'.format(now_x,now_x))
            print(paste_x[i],end=' ')
        #=============================#
        
        plt.xscale('log')
        ax1.set_xlabel(x_title,fontsize=25)
        ax1.set_ylabel('Avg KPS',fontsize=25)
        ax2.set_ylabel('AVG. GPU Util(%)',fontsize=25)
        plt.xticks(origin_x,paste_x,fontsize=25)
        ax1.minorticks_off()
        ax1.grid(True)

        #===limit=====#
        #ax1.set_ylim(0)
        ax2.set_ylim(0,100)
        #=============#


    
        plt.savefig(save_name)
        plt.close()



    elif(graph_type==3):
        data1=result
        global_data=data1[data1['App']=='convolution_global']
        local_data=data1[data1['App']=='convolution_local']

        global_data=global_data[global_data['filter']==7]
        local_data=local_data[local_data['filter']==7]
        #===================저장 이름/그래프형태/타이틀 지정=============================#
        save_name=dir_path+'/convolution_local_N_global_Filter_7x7.png'
        title='Convolution Mat [5000x6000] Local & Global Filter 7x7 Ver.'
        #===========================================================================#
    
        ax1=plt.figure(figsize=(18,7))
        gs=gridspec.GridSpec(nrows=1,ncols=1,bottom=0.15,top=0.92)
        ax1=plt.subplot(gs[0])
        ax2=ax1.twinx()
        ax1.set_title(title,fontsize=25)
        lines=[]
        labels=[]

        line1=ax1.plot(global_data['sub_x'],global_data['avg_kps'],color=colors1[0],linewidth=2)
        lines.append(line1[0])
        labels.append('global KPS')
        line2=ax2.plot(global_data['sub_x'],global_data['Avg_Gpu_Util'],color=colors1[1],linewidth=2)
        lines.append(line2[0])
        labels.append('global GPU Util(%)')

        line3=ax1.plot(local_data['sub_x'],local_data['avg_kps'],color=colors1[2],linewidth=2)
        lines.append(line3[0])
        labels.append('local KPS')
        line4=ax2.plot(local_data['sub_x'],local_data['Avg_Gpu_Util'],color=colors1[3],linewidth=2)
        lines.append(line4[0])
        labels.append('local GPU Util(%)')


        plt.legend(lines,labels,fontsize=12,loc='upper left')


        #======================================글씨============================================#
        '''
        plt.text(x=400,y=0.35,s='GUI KPS Local: 4x4',  color=colors[2],weight='bold',rotation=0,fontsize=14)
        plt.text(x=400,y=0.65,s='GUI KPS Local: 8x8',  color=colors[3],weight='bold',rotation=0,fontsize=14)
        '''
        #=====================================================================================#

        x_title='[Row x Col]\nSubkernel Size'
        #===== X 값에 넣을 어디 숫자? =====#
        origin_x=[]
        for i in range(0,len(data1)):
            now_subx=data1.loc[i,'sub_x']
            if(now_subx in origin_x):
                continue
            origin_x.append(data1.loc[i,'sub_x'])
        origin_x.sort()
        print(origin_x)
        #==============================#


        #== origin_x에 덮어 씌울 값은? ==#
        paste_x=[] 
        for i in origin_x:
            now_string='{}x{}'.format(i,6000)
            print(now_string)
            paste_x.append(now_string)
        #=============================#
        plt.xscale('log')
        ax1.set_xlabel(x_title,fontsize=25)
        ax1.set_ylabel('Avg KPS',fontsize=25,color=colors1[0])
        ax2.set_ylabel('AVG. GPU Util(%)',fontsize=25,color=colors1[1])
        plt.xticks(origin_x,paste_x,fontsize=25)
        ax1.minorticks_off()
        ax1.grid(True)

        #===limit=====#
        #ax1.set_ylim(0)
        ax2.set_ylim(40,100)
        #=============#


    
        plt.savefig(save_name)
        plt.close()