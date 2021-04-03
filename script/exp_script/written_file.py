#!/usr/bin/env python3
import os
import argparse
import sys

def read_file(scenario_path,A=None,B=None,C=None,D=None,E=None,F=None,G=None,H=None,I=None,J=None,debug=False):

    try:
        if(os.path.isabs(scenario_path)==False):
            scenario_path=os.path.abspath(os.path.normcase(scenario_path))
    except:
        print('[Error] I can\'t find scenario file at written_file.py')
        sys.exit(1)

    fp=open(scenario_path,'r')
    scenario_dir=os.path.dirname(scenario_path)
    if(debug):
        print('[scenario_dir] '+scenario_dir)
        print('[scenario_path] '+scenario_path)
    while True:
        line=fp.readline().strip()
        if not line:
            break
        if line[0]=='#':
            continue
        try:
            option,value=(line.strip()).split('	')
            if(debug):
                print('[option] '+option,end=' ')
                print(',   [value] '+value)

            if option == 'expr_schedule':
                if(debug):
                    print('[schedule file] '+scenario_dir+'/'+value)
                schedule(scenario_dir+'/'+value,A,B,C,D,E,F,G,H,I,J,debug)
        except ValueError:
            print('[Error [{}] format of scenario is like OPTION VALUE'.format(option))
            sys.exit(1)
            
    fp.close()


def schedule(path,A=None,B=None,C=None,D=None,E=None,F=None,G=None,H=None,I=None,J=None,debug=False):
    if(debug):
        print('[Read file] '+path)
        print('[Write file] '+path+'_exp')
    fp=open(path,'r')
    fw=open(path+'_exp','w')
    while True:
        line=fp.readline().strip()
        if(debug):
            print('[Read file] '+path+'[Read Line] '+line)
        if not line:
            break
        if line[0]=='#':
            continue
        
        #ex)[APP Execute Command -args1 -args2 ]\t[Start]\t[End|inf]\t[ENV1;ENV2;ENV3...]
        #ex)~/bin/clExample -A -B -C -D	0	inf	PATH=/home/root/nfs/experiment/matmul/gpgpu/example:$PATH;LD_PRELOAD={}/../../gpgpu/lib/libclsched.so
        if(A!=None):
            line=line.replace('-A',str(A))
        if(B!=None):
            line=line.replace('-B',str(B))
        if(C!=None):
            line=line.replace('-C',str(C))
        if(D!=None):
            line=line.replace('-D',str(D))
        if(E!=None):
            line=line.replace('-E',str(E))
        if(F!=None):
            line=line.replace('-F',str(F))
        if(G!=None):
            line=line.replace('-G',str(G))
        if(H!=None):
            line=line.replace('-H',str(H))
        if(I!=None):
            line=line.replace('-I',str(I))
        if(J!=None):
            line=line.replace('-J',str(J))
        if(debug):
            print('[Changed line]: '+line)
        fw.write(line+'\n')

    fp.close()
    fw.close()

    