# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 11:17:38 2018

@author: ZeroPC
"""
from __future__ import division
import pprint
import json
import pyomo.environ as pe
from pyomo.opt import SolverFactory
from pyomo.core import Var
import os 
import numpy as np
import time
import datetime
import random
import datetime
from pyomo.environ import *
#

#
'''部分变量描述不清楚的，可以用print打印一下看看具体是什么，结合我的变量名字和用处应该可以理解'''
'''数据检查函数'''#selected_tasks = plan_cc ，process_time = rule_process_time ，code_device = rule_code_device，transport_time = rule_transport_time
def task_inspect(selected_tasks,process_time,code_device,transport_time):
    #task预处理
    list_jb=['D','B','R','L','U','T']
    l=len(selected_tasks)  #len是获取字典长度，即有多少个键-值对
    task_PNON=[]
    task_SG=[]
    task_FINERY_PATH_ID=[]
    task_CC_START_TIME=[]
    for i in range(l):
        task_PNON.append(selected_tasks[i]['PONO'])
        task_SG.append(selected_tasks[i]['SG'])
        task_FINERY_PATH_ID.append(selected_tasks[i]['FINERY_PATH_ID'])
        if selected_tasks[i]['CC_START_TIME']!='':
            task_CC_START_TIME.append(selected_tasks[i]['CC_START_TIME'])
    #process_time预处理
    process_time_l=len(process_time)
    process_time_SG=[]
    for i in range(process_time_l): 
        process_time_SG.append(process_time[i]['SG'])
    #SG判断
    len_SG=len(task_SG)
    for i in range(len_SG):
        if task_SG[i] not in process_time_SG:
            print("警告：加工时间数据中不存在您所输入的浇次，请核对staic_plan_cc数据：",task_SG[i])
    #工序判定
    len_FINERY_PATH_ID=len(task_FINERY_PATH_ID)
    for i in range(len_FINERY_PATH_ID):
        for j in range(len(task_FINERY_PATH_ID[i])):
           if task_FINERY_PATH_ID[i][j] not in list_jb:
               print("警告：此工序为非法工序号：",task_FINERY_PATH_ID[i][j])
    #预计连铸开始时间判定
    nowdate = datetime.datetime.now()  #返回当前系统时间
    nowdate = nowdate.strftime("%Y-%m-%d %H:%M:%S")   #时间格式化
    for i in range(len(task_CC_START_TIME)) :
        if task_CC_START_TIME[i]<nowdate:   #计划开工时间与现在时间作比较
            print("警告，您输入的连铸机预计开始时间为过去时间",task_CC_START_TIME[i])

#staic_Plan_CC处理函数目地是让无序的task按照有序的'CC_ID'进行排列
def sort_task(selected_tasks):
    list_501=[]
    list_502=[]
    list_503=[]
    len_task=len(selected_tasks)
    for i in range(len_task):
        if selected_tasks[i]['CC_ID']=='501':
          list_501.append(selected_tasks[i])
        if selected_tasks[i]['CC_ID']=='502':
          list_502.append(selected_tasks[i])
        if selected_tasks[i]['CC_ID']=='503':
          list_503.append(selected_tasks[i])
    list_501 = sorted(list_501,key = lambda e:e.__getitem__('PLAN_NUMBER'))
    list_502 = sorted(list_502,key = lambda e:e.__getitem__('PLAN_NUMBER'))
    list_503 = sorted(list_503,key = lambda e:e.__getitem__('PLAN_NUMBER'))
    return list_501+list_502+list_503


'''输入是selected_tasks。
输出list_jiaoci_start（每个浇次开始炉次）, list_luci（所有炉次）, list_jiaoci_end（每个浇次结束的炉次）,list_remove_end（每个浇次去除末尾炉次的剩下炉次）,
list_pono_cast（每个炉次所对应的pono号）,list_CC_ID（#连铸变化的pono）,list_CC_START_TIME（连铸机开始的时间与pono的集合）'''
def task_pack(selected_tasks):#用于打包各个浇次中炉次的集合
    selected_tasks=sort_task(selected_tasks)#这里调用上一个函数进行排序
    list_pono_cast=[[0 for i in range(2)]for i in range(len(selected_tasks))]
    list_CC_ID=[]#连铸变化的pono
    #4.1新改的begin    
    list_CC_START_TIME=[]#连铸机预计开始时间
    list_CC_START_TIME_temp=[]
    for i in range(len(selected_tasks)):
        if i==0:
             
             list_CC_START_TIME_temp.append(selected_tasks[i]['PONO'])
             list_CC_START_TIME_temp.append(selected_tasks[i]['CC_START_TIME'])
             list_CC_START_TIME.append(list_CC_START_TIME_temp)
             list_CC_START_TIME_temp=[]
#把 selected_tasks 里每一个 浇次的第一个炉次的 PONO（制造命令号）和 CC_START_TIME（连铸机预计开 始时间）送给 list_CC_START_TIME
        else :
            if selected_tasks[i]['CC_ID']!=selected_tasks[i-1]['CC_ID'] :
                
                list_CC_START_TIME_temp.append(selected_tasks[i]['PONO'])
                list_CC_START_TIME_temp.append(selected_tasks[i]['CC_START_TIME'])
                list_CC_START_TIME.append(list_CC_START_TIME_temp)
                list_CC_START_TIME_temp=[]
#4.1新改的 end
    for i in range(len(selected_tasks)):
        list_pono_cast[i][0]=selected_tasks[i]['PONO']
        list_pono_cast[i][1]=selected_tasks[i]['CC_ID']
        if i>1:
            if selected_tasks[i]['CC_ID']!=selected_tasks[i-1]['CC_ID'] :
                
                list_CC_ID.append(selected_tasks[i-1]['PONO'])
    
    list_jiaoci_start=[]#所有浇次开始炉次
    list_luci=[]#所有炉次号
    list_jiaoci_end=[]#所有浇次末尾炉次集合
    list_remove_end=[]#所有去除末尾炉次的剩下炉次的集合
    for i in range(len(selected_tasks)):
        list_luci.append(selected_tasks[i]['PONO'])#把 select_tasks 的 PONO 送给 list_luci
        if i==0:
            list_jiaoci_start.append(selected_tasks[i]['PONO'])#把 501、502 和 503 对应的第一个炉次送给 list_jiaoci_start
        elif  selected_tasks[i]['CC_IDENTIFY']=='T' or selected_tasks[i-1]['CC_ID']!=selected_tasks[i]['CC_ID']:
            list_jiaoci_start.append(selected_tasks[i]['PONO'])
            list_jiaoci_end.append(selected_tasks[i-1]['PONO'])
        if i==len(selected_tasks)-1:
            list_jiaoci_end.append(selected_tasks[i]['PONO'])#对应的最后一个炉次送给 list_jiaoci_end
    
    for i in range(len(list_luci)):
           if list_luci[i] in list_jiaoci_end:
               a=0#啥也不做的意思
           else:
                list_remove_end.append(list_luci[i])#，把去除所有末尾炉次的剩下炉次送给 list_remove_end
    return  list_jiaoci_start, list_luci, list_jiaoci_end,list_remove_end,list_pono_cast,list_CC_ID,list_CC_START_TIME

def addtime(date1,date2,date3):
    date1=datetime.datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2=datetime.datetime.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date3=datetime.datetime.strptime(date3,"%Y-%m-%d %H:%M:%S")
    return date2-date1+date3
#时间转换函数，目的是为了把我们的计算出来的相对时间转化为实际的时间
def time_add(s):
    timeArray = time.localtime(s)#接受一个时间戳，并把它转化为一个当前时间的元组
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)#将一个时间元组转换为格式化的时间字符
    nowdate = datetime.datetime.now() # 获取系统当前时间
    nowdate = nowdate.strftime("%Y-%m-%d %H:%M:%S") # 格式化时间
    date1 =otherStyleTime
    date2 = r'1970-01-01 08:00:00'
    data3 =nowdate 
    return addtime(date2,date1,data3)
#调度模型函数 pyomo语言建立，需要传入三个辅助列表list_sb,list_CC_ID,list_pono_cast
def model_main(list_sb,list_CC_ID,list_pono_cast):
    k_zhidian={'101': 'D', '102': 'D', '103': 'D', '201': 'B', '301': 'R', '302': 'R', '401': 'W', '402': 'W', '403': 'W', '501': 'T', '502': 'T', '503': 'T', '202': 'B', '203': 'B', '303': 'R', '312': 'L', '311': 'L', '321': 'U'}
    
    model = AbstractModel("diaoduxin")
    
    model.I=Set()
    model.I7=Set()
    #每个浇次开始的炉次
    model.I1=Set()
    #i+1的炉次
    model.I2=Set()
    #每个浇次结束的炉次
    model.I3=Set()
    #model.I4=Set()
    
    model.J=Set()
    model.J2=Set()
    model.J3=Set()
    
    model.K=Set()
    model.A=Set(within=model.I*model.J)
    model.A2=Set(within=model.I*model.J)
    
    '''
    model.dual = pe.Suffix(direction=pe.Suffix.IMPORT_EXPORT)
    '''
    #加工时间Pij,运输时间Tj,j+1,计划开浇时间dn
    model.p=Param(model.A,within=NonNegativeReals)       #在第j阶段炉次i的加工时间
    model.T=Param(model.J,model.J,within=NonNegativeReals)#炉次在第j阶段和第j+1阶段之间运输所需要的的标准时间
    model.d=Param(model.I1,within=NonNegativeReals)       #浇次的计划开浇时间
    #决策变量，
    model.x= Var(model.I,model.J,model.K, within=Binary) #炉次i在阶段j的第k台设备上是1，否则为0
    model.y= Var(model.I,model.I,model.J, within=Binary) #炉次i提前r在阶段j被处理时是1，否则为0
    model.t= Var(model.A, within=NonNegativeIntegers)    #炉次i在第j阶段的作业开始时间
    model.tu= Var(model.A, within=NonNegativeIntegers)   #浇次开浇提前时间
    model.td= Var(model.A, within=NonNegativeIntegers)   #浇次开浇延迟时间
    def obj_rule(model):
       
     
        return sum(model.t[i,'T']-model.t[i,'D'] for i in model.I )+10*sum(model.tu[i1,'T'] for i1 in model.I1 )+10*sum(model.td[i1,'T'] for i1 in model.I1) 
    model.obj = Objective(rule=obj_rule,sense=minimize)
    
    def list_next(list1,i):#计算列表下一个元素
        return list1[list1.index(i)+1]
    
    
    list_jb=['D','B','R','L','U','T']
    def getTwoDimensionListIndex(L,value): # ？？？
     
        data = [data for data in L if data[0]==value]  
        index = L.index(data[0])  
        return index
    
    def con_rule(model,i,j):
        if model.p[i,j]==0:
            a=0
        else:
            a=1
        #炉次i在第j+1阶段作业开始时间减去炉次i在第j阶段作业开始时间要大于炉次i在第j阶段的加工时间与第j工序到第j+1工序的运输时间之和
        return (model.t[i,list_next(list_jb,j)]-model.t[i,j]-model.p[i,j]-a*model.T[j,list_next(list_jb,j)] )>=0
        
    model.con = Constraint(model.A2,rule=con_rule)
    
    def con_rule1(model,i):
        #保证连续浇铸
        return (model.t[list_next(list_sb,i),'T']-model.t[i,'T']-model.p[i,'T'])==0
        
    model.con1 = Constraint(model.I2, rule=con_rule1)
    def con_rule2(model,i):
        if str(i) not in list_CC_ID:
            #某一个浇次开浇的炉次开始时间减去上一个浇次末炉次的加工开始时间和工作时间要大于浇次之间更换结晶器所用的时间
            return (model.t[list_next(list_sb,i),'T']-model.t[i,'T']-model.p[i,'T'])>=40
        return Constraint.Skip
    model.con2 = Constraint(model.I3, rule=con_rule2)
    #浇铸阶段第i个炉次的加工开始时间减去计划开浇时间等于提前时间或延迟时间
    def con_rule3(model,i):
        return (model.t[i,'T']-model.tu[i,'T']+model.td[i,'T']==model.d[i])
    model.con3 = Constraint(model.I1, rule=con_rule3)
    #一个炉次同一时间只能工作在一台设备上，只能处于一种工作状态
    def con_rule4(model,i,j):
        return sum(model.x[i,j,k] for k in model.K if k_zhidian[str(k)]==j )==1
    model.con4 = Constraint(model.I,model.J2,rule=con_rule4)
    # Xijk是0-1变量
    def con_rule44(model,i,k):
        if list_pono_cast[getTwoDimensionListIndex(list_pono_cast, str(i))][1]==str(k):
            return model.x[i,'T',k]==1
        return Constraint.Skip
    model.con44 = Constraint(model.I,model.K, rule=con_rule44)
    #要么炉次i提前炉次r，要么炉次r提前炉次i
    def con_rule5(model,i,r,j):
        if i!=r:
            return (model.y[i,r,j]+model.y[r,i,j])==1 
        return Constraint.Skip
       
    model.con5 = Constraint(model.I,model.I,model.J2, rule=con_rule5)
    #
    #同一台设备同一时间只能加工一个炉次
    def con_rule6(model,i,r,j,k):
        #for k in model.K:
        if k_zhidian[str(k)]==j and i!=r :                    
            return (model.t[r,j]-model.t[i,j]-model.p[i,j]+10000*(3-model.x[i,j,k]-model.x[r,j,k]-model.y[i,r,j]))>=0
        return Constraint.Skip
    
    model.con6 = Constraint(model.I,model.I,model.J2,model.K, rule=con_rule6)
    return model
#这是将计算出来的结果转化成字典输出，为了使得能应用于甘特图。
'''其中task_test就是输入的task，process_time是加工时间（为了计算每个工序结束时间用的），list_lie,list_lie2,list_hang是对solver求解的结果保存的列表
jiaoci_beigin_time1是我们计算出来的每个炉次的预计开胶时间（这块注意是每个炉次的，因为是后改的所以变量名字是jiaoci_beigin_time1）
输出list_result是结果列表'''
def result_list_to_result(task_test,process_time,list_lie,list_lie2,list_hang,jiaoci_beigin_time1):
    result={
            "PLAN_SAVE_TIME" : "",
            "PONO" : "",
            "HTNO" : 330351,
            "SG" : "",
            "FINERY_PATH_ID" : "",
            "LD_1_WAIT_ID" : "",
            "LD_1_ID" : "",
            "LD_2_ID" : "",
            "STOVE_PROCESS_NO" : "",
            "P_PROCESS_NO" : "",
            "BA_ID" : "203",
            "FINERY_1_ID" : "",
            "FINERY_2_ID" : "",
            "FINERY_3_ID" : "",
            "FINERY_4_ID" : "",
            "FINERY_1_PROCESS_NO" : "",
            "FINERY_2_PROCESS_NO" : "",
            "FINERY_3_PROCESS_NO" : "",
            "FINERY_4_PROCESS_NO" : "",
            "CAST_1_WAIT_ID" : "",
            "CAST_1_ID" : "",
            "CAST_2_ID" : "",
            "CAST_1_PROCESS_NO" : "",
            "CASTNO_POUR" : "",
            "INGOT_TYPE" : "",
            "INGOT_COU" : 2,
            "LD_1_WAIT_START_TIME" : "",
            "LD_1_WAIT_END_TIME" : "",
            "LD_1_START_TIME" : "",
            "LD_1_BLOW_END_TIME" : "",
            "LD_1_TAPPING_START_TIME" : "",
            "LD_1_END_TIME" : "",
            "LD_2_WAIT_START_TIME" : "",
            "LD_2_WAIT_END_TIME" : "",
            "LD_2_START_TIME" : "",
            "LD_2_BLOW_END_TIME" : "",
            "LD_2_TAPPING_START_TIME" : "",
            "LD_2_END_TIME" : "",
            "BA_START_TIME" : "",
            "BA_END_TIME" : "",
            "FINERY_1_START_TIME" : "",
            "FINERY_1_END_TIME" : "",
            "FINERY_2_START_TIME" : "",
            "FINERY_2_END_TIME" : "",
            "FINERY_3_START_TIME" : "",
            "FINERY_3_END_TIME" : "",
            "FINERY_4_START_TIME" : "",
            "FINERY_4_END_TIME" : "",
            "CAST_1_WAIT_START_TIME" : "",
            "CAST_1_WAIT_END_TIME" : "",
            "CAST_1_START_TIME" : "",
            "CAST_1_END_TIME" : "",
            "CAST_2_START_TIME" : "",
            "CAST_2_END_TIME" : "",
            "CAST_TYPE" : 1,
            "PLAN_SOURCE" : 1,
            "PLAN_STYLE" : 1,
            "PLAN_STATUS" : 6,
            "LADLE_STATUS" : "",
            "DETAILS" : "",
            "D_ARRIVE_TURN_TIME" : "",
            "D_REAL_STATUS_ID" : "",
            "D_STATUS_TIME" : "",
            "D_TIME_SUBTRACT" : "",
            "D_DECISION_SG" : "",
            "D_RETURN_ID" : "",
            "D_DISTURB_TIME" : "",
            "D_DISTURB_TEMP" : "",
            "D_DISTURB_CC" : "",
            "D_DISTURB_SG" : "",
            "D_DISTURB_DEVICE" : "",
            "D_DISTURB_OTHERS" : "",
            "D_FIRST_STRATEGY_TIME" : "",
            "D_FIRST_SIMILARITY_TIME" : "",
            "D_SECOND_STRATEGY_TIME" : "",
            "D_SECOND_SIMILARITY_TIME" : "",
            "D_THIRD_STRATEGY_TIME" : "",
            "D_THIRD_SIMILARITY_TIME" : "",
            "D_FIRST_STRATEGY_TEMP" : "",
            "D_FIRST_SIMILARITY_TEMP" : "",
            "D_SECOND_STRATEGY_TEMP" : "",
            "D_SECOND_SIMILARITY_TEMP" : "",
            "D_THIRD_STRATEGY_TEMP" : "",
            "D_THIRD_SIMILARITY_TEMP" : "",
            "D_FIRST_STRATEGY_CC" : "",
            "D_FIRST_SIMILARITY_CC" : "",
            "D_SECOND_STRATEGY_CC" : "",
            "D_SECOND_SIMILARITY_CC" : "",
            "D_THIRD_STRATEGY_CC" : "",
            "D_THIRD_SIMILARITY_CC" : "",
            "OPTIMIZATION_STYLE" : "",
            "CC_IDENTIFY" : "",
            "ROWID" : "AAANHaAAGAAAANWAAA"}
      #鍋氫竴涓炕璇戝瓧鍏?瀹屾垚瀛楁瘝涓庢暟瀛椾箣闂寸殑鍜岃浆鍖?
    zd_fy={'101':'D','102':'D','103':'D','201':'B','202':'B','203':'B','301':'R','302':'R','303':'R','311':'L','312':'L','321':'U','401':'W','402':'W','403':'W','501':'T','502':'T','503':'T','521':'T'}
  
    
    list_result=[]#结果列表
    #给 result_a 里的 PONO、SG、FINERY_PATH_ID、LD_1_ID、BA_ID、 FINERY_1_ID、FINERY_2_ID、FINERY_3_ID 和 CAST_1_ID 分别赋值 task_test 的 PONO、SG、FINERY_PATH_ID 和 list_lie[][0-5]
    for i in range(len(task_test)): #task_test就是输入的task
        result_a=result.copy()  #浅拷贝，result字典中的key不变，只会改变value
        result_a["PONO"]=task_test[i]["PONO"]
        result_a["SG"]=task_test[i]["SG"]
        result_a["FINERY_PATH_ID"]=task_test[i]["FINERY_PATH_ID"].strip()
        #鍚勪釜宸ュ簭鐨勫啓鍏?
       
        string=result_a["FINERY_PATH_ID"]
        for r in range(len(list_lie)):
            if task_test[i]["PONO"]==str(list_lie[r][len(list_hang)-1]):
                result_a["LD_1_ID"]=str(list_lie[r][0])
                result_a["BA_ID"]=str(list_lie[r][1])
                if 'R' in string:
                    result_a["FINERY_1_ID"]=str(list_lie[r][2])
                if 'L' in string:
                    result_a["FINERY_2_ID"]=str(list_lie[r][3])
                if 'U' in string:
                    result_a["FINERY_3_ID"]=str(list_lie[r][4])
                
                result_a["CAST_1_ID"]=str(list_lie[r][5])
       
    
            
        # result_a 里面的 LD_1、BA、FINERY_1、FINERY_2、FINERY_3 和 CAST_1 的 START_TIME 和 END_TIME 进行赋值    
        for m in range(len(list_lie2)):#鏇存敼 B 鍜屽畾鐨刱ey
            if task_test[i]["PONO"]==str(list_lie2[m][0]) and zd_fy[str(list_lie2[m][1])]=='D':
                result_a["LD_1_START_TIME"]=str(time_add(int(list_lie2[m][2])*60))
                for t in range(len(process_time)):
                    if task_test[i]['SG']==process_time[t]['SG'] and  str(list_lie2[m][1])==process_time[t]['DEVICE_ID'] :
                        result_a["LD_1_END_TIME"]=str(time_add(int(list_lie2[m][2])*60+int(process_time[t]['PROCESS_TIME'])*60))
                        
            
            elif task_test[i]["PONO"]==str(list_lie2[m][0]) and zd_fy[str(list_lie2[m][1])]=='B':
                result_a["BA_START_TIME"]=str(time_add(int(list_lie2[m][2])*60))
                for t in range(len(process_time)):
                    if task_test[i]['SG']==process_time[t]['SG'] and  str(list_lie2[m][1])==process_time[t]['DEVICE_ID'] :
                        result_a["BA_END_TIME"]=str(time_add(int(list_lie2[m][2])*60+int(process_time[t]['PROCESS_TIME'])*60))
                        
            
            elif task_test[i]["PONO"]==str(list_lie2[m][0]) and zd_fy[str(list_lie2[m][1])]=='R':
                result_a["FINERY_1_START_TIME"]=str(time_add(int(list_lie2[m][2])*60))
                for t in range(len(process_time)):
                    if task_test[i]['SG']==process_time[t]['SG'] and  str(list_lie2[m][1])==process_time[t]['DEVICE_ID'] :
                        result_a["FINERY_1_END_TIME"]=str(time_add(int(list_lie2[m][2])*60+int(process_time[t]['PROCESS_TIME'])*60))
                        
                        
            elif task_test[i]["PONO"]==str(list_lie2[m][0]) and zd_fy[str(list_lie2[m][1])]=='L':
                result_a["FINERY_2_START_TIME"]=str(time_add(int(list_lie2[m][2])*60))
                for t in range(len(process_time)):
                    if task_test[i]['SG']==process_time[t]['SG'] and  str(list_lie2[m][1])==process_time[t]['DEVICE_ID'] :
                        result_a["FINERY_2_END_TIME"]=str(time_add(int(list_lie2[m][2])*60+int(process_time[t]['PROCESS_TIME'])*60))
                        
            
            elif task_test[i]["PONO"]==str(list_lie2[m][0]) and zd_fy[str(list_lie2[m][1])]=='U':
                result_a["FINERY_3_START_TIME"]=str(time_add(int(list_lie2[m][2])*60))
                for t in range(len(process_time)):
                    if task_test[i]['SG']==process_time[t]['SG'] and  str(list_lie2[m][1])==process_time[t]['DEVICE_ID'] :
                        result_a["FINERY_3_END_TIME"]=str(time_add(int(list_lie2[m][2])*60+int(process_time[t]['PROCESS_TIME'])*60))
                        
            
            elif task_test[i]["PONO"]==str(list_lie2[m][0]) and zd_fy[str(list_lie2[m][1])]=='T':
                result_a["CAST_1_START_TIME"]=str(time_add(int(list_lie2[m][2])*60))
                
                temp=jiaoci_beigin_time1[getTwoDimensionListIndex(jiaoci_beigin_time1,task_test[i]['PONO'])][1]
                
                result_a["CAST_1_END_TIME"]=str(time_add(int(list_lie2[m][2])*60+int(temp)*60))#绛?01绯诲垪鎭㈠涔嬪悗鑷細杩涜淇鐢ㄤ笂闈㈤偅涓嚱鏁?
                        #print(function.time_add(int(list_lie2[m][2])*60+int(process_time[t]['PROCESS_TIME'])*60))
        
        list_result.append(result_a)
    return list_result
def getTwoDimensionListIndex(L,value): #获得二维列表某个元素所在的index 
         
        data = [data for data in L if data[0]==value]  
        index = L.index(data[0])  
        return index
#连铸工序时间
'''file是输入的task，list_jiaoci_start,list_luci分别是浇次开始的炉次和全部炉次的集合。
输出是各个炉次的连铸工序的加工所用时间'''
def Calculate_continuous_castingtime(file,list_jiaoci_start,list_luci):#连铸工序时间
    task=file
    p_list=[]
    for i in range(len(task)):
        w=230 #钢水质量
        a=task[i]["THICKNESS"]  #输出板坯厚度
        wide_odd=(task[i]["LOT_ODD_WIDTH1"]+task[i]["LOT_ODD_WIDTH2"])/2  #奇流板坯宽度
        wide_even=(task[i]["LOT_EVEN_WIDTH1"]+task[i]["LOT_EVEN_WIDTH2"])/2  #偶流板坯宽度
        v=1.2 #拉速
        if(task[i]["PONO"] in list_jiaoci_start):
            p=(w*1e6)/(7.8*a*(wide_odd+wide_even)*(v-0.2))
            p_list.append([task[i]["PONO"],int(p)])
        else:
            front=list_luci.index(task[i]["PONO"])-1
            last_wide_odd=(task[front]["LOT_ODD_WIDTH1"]+task[front]["LOT_ODD_WIDTH2"])/2    #上一炉次奇流板坯宽度
            last_wide_even=(task[front]["LOT_EVEN_WIDTH2"]+task[front]["LOT_EVEN_WIDTH2"])/2  #上一炉次偶流板坯宽度
            wide=wide_odd+wide_even+last_wide_odd+last_wide_even
            p=(w*1e6-31.2*a*wide)/(3.9*a*wide*(v-0.2))+8/(v-0.2)
            p_list.append([task[i]["PONO"],int(p)])
    p_list2=[]
    for i in range(len(list_luci)):
        p_list2.append(p_list[getTwoDimensionListIndex(p_list,list_luci[i])])
        
        
    return p_list2
#data数据生成文件，输入变量同上有具体解释
def data(task_test,process_time,code_device,transport_time,list_jiaoci_start, list_luci, list_jiaoci_end,list_remove_end,list_pono_cast,list_CC_ID,list_CC_START_TIME):
    cast_time=Calculate_continuous_castingtime(task_test,list_jiaoci_start,list_luci)#yang
    fo = open("foo1.dat", "w")
    num=len(list_luci)
    lu=len(list_luci)#
    lu_num=list_luci#炉次的全部集合
    
    fo.write('set I :=')
    for i in range(num):
        fo.write(str(lu_num[i])+" ")
    fo.write(';') 
    list_sb=[]
    for p in lu_num:
        list_sb.append(int(p))
        
    
    fo.write("\n")
    fo.write('set I1 :=')
    jiaoci_begin=list_jiaoci_start
    #num1=0      
    for j in  range(len(jiaoci_begin)):
        fo.write(str(jiaoci_begin[j])+" ")
    fo.write(';')
    
    
    fo.write("\n")
    fo.write('set I2 :=')
    for j in  range(len(list_remove_end)):
        fo.write(str(list_remove_end[j])+" ")
    fo.write(';')
    
    # #各个浇次末尾炉次算法
    
    fo.write("\n")
    fo.write('set I3 :=')
    for j in  range(len(list_jiaoci_end)-1):#鍑忓幓1鐨勭洰鍦版槸涓轰簡婊¤冻鏈€鍚庝竴涓倝娆℃湯鐢ㄤ笉涓婄殑瑕佹眰
        fo.write(str(list_jiaoci_end[j])+" ")
    fo.write(';')
    fo.write("\n") 
    
    
    DEVICE_ID=[]#宸ュ簭璁惧鍙?
    PROCESS_TIME=[]#宸ュ簭璁惧鍔犲伐鏃堕棿
    for i in range(len(process_time)):
        if process_time[i]['DEVICE_ID'] in DEVICE_ID:
            aaaaaaaaaa=0
        else:
            DEVICE_ID.append(process_time[i]['DEVICE_ID'])
            PROCESS_TIME.append(process_time[i]['PROCESS_TIME'])
    
    jg_time={}#鍚勭宸ュ簭瀵瑰簲鍔犲伐鏃堕棿鈥斺€斿瓧鍏稿舰寮忚〃绀?
    for i in range(len(DEVICE_ID)):
        jg_time[DEVICE_ID[i]]=PROCESS_TIME[i]
    
    
    jiagong_paixu_int=[]#鎸夐『搴忕殑鍔犲伐鎺掑簭鍙?int鍨?
    jiagong_paixu_str=[]#鎸夐『搴忕殑鍔犲伐鎺掑簭鍙?string鍨?
    for i in DEVICE_ID:
        jiagong_paixu_int.append(int(i))
    jiagong_paixu_int.sort()
    for i in jiagong_paixu_int:
        jiagong_paixu_str.append(str(i))
    
    lujing=[[0 for col in range(2)] for row in range(len(code_device))]  #鍒涘缓浜岀淮鍒楄〃锛? yulin?
    
    for i in range(len(code_device)):
        lujing[i][0]=code_device[i]['FINERY_SHOW_ID']
        lujing[i][1]=code_device[i]['DEVICE_ID']
    #lujing[len(code_device)][0]='U'
    #lujing[len(code_device)][1]='321'#杩欐槸鍥犱负鏁版嵁搴撶殑闂
    
    
    guxu_sy=['D','B','R','L','U','T']
    guxu_sy1=['R','L','U']
    
    
    
    lujing_x=np.array(lujing)#np  zhuanghuan 
    fo.write('set J :=')
    for i in range(len(guxu_sy)):
        fo.write(str(guxu_sy[i])+' ')
    fo.write(';')
    fo.write("\n")
    fo.write('set J2 :=')
    for i in range(len(guxu_sy)-1):
        fo.write(str(guxu_sy[i])+' ')
    fo.write(';')
    fo.write("\n")
    
    fo.write('set K :=')
    for i in range(lujing_x.shape[0]):
        fo.write(str(lujing[i][1])+' ')
    fo.write(';')
    fo.write("\n")
    
    fo.write('set A :=')
    
    gongxushu=len(guxu_sy)
    for i in range(lu):
        lishi=[]
        for y in guxu_sy1:
            lishi.append(y)
        for j in range(gongxushu-2):#zhelide 4 shihuibiande 
            if j<2:
                fo.write('('+task_test[i]['PONO']+','+guxu_sy[j]+')'+' ')
            elif j==2:
                m1=len(task_test[i]['FINERY_PATH_ID'].strip())
                
                for n in range(m1):
                    
                    
                    fo.write('('+task_test[i]['PONO']+','+((task_test[i]['FINERY_PATH_ID']).strip())[int(n)]+')')
                    if (task_test[i]['FINERY_PATH_ID']).strip()[int(n)]=='I':
                        lishi.remove('L')
                    else:
                        lishi.remove((task_test[i]['FINERY_PATH_ID'].strip())[n])
                    
                    
                for n in range(3-m1):
                    fo.write('('+task_test[i]['PONO']+','+lishi[n]+')')
            elif j==gongxushu-3:
                fo.write('('+task_test[i]['PONO']+','+guxu_sy[gongxushu-1]+')')#zheli de 2shiyao gaide 
    fo.write(';')
    fo.write("\n")
    
    fo.write('set A2 :=')
    
    gongxushu=len(guxu_sy)
    for i in range(lu):
        lishi=[]#guxu_sy1鐨勫鍒跺搧
        for y in guxu_sy1:
            lishi.append(y)
        for j in range(gongxushu-2):#zhelide 4 shihuibiande 
            if j<2:
                fo.write('('+task_test[i]['PONO']+','+guxu_sy[j]+')'+' ')
            elif j==2:
                m1=len(task_test[i]['FINERY_PATH_ID'].strip())
                
                for n in range(m1):
                    
                    
                    fo.write('('+task_test[i]['PONO']+','+((task_test[i]['FINERY_PATH_ID']).strip())[int(n)]+')')
                    if (task_test[i]['FINERY_PATH_ID']).strip()[int(n)]=='I':
                        lishi.remove('L')
                    else:
                        lishi.remove((task_test[i]['FINERY_PATH_ID'].strip())[n])
                    
                for n in range(3-m1):
                    fo.write('('+task_test[i]['PONO']+','+lishi[n]+')')
             
    fo.write(';')
    fo.write("\n")
    
    
    fo.write('param :p:=')
    fo.write("\n") 
    for i in range(lu):
        lishi=[]#guxu_sy1鐨勫鍒跺搧
        for y in guxu_sy1:
            lishi.append(y)
           
        for j in range(gongxushu-2):#zhelide 4 shihuibiande 
            if j<2:
                fo.write(task_test[i]['PONO']+' '+guxu_sy[j])
                for o in range(lujing_x.shape[0]):
                    if lujing[o][0]==guxu_sy[j]:
                        lu_index=o#zheli zhi xuan ze yige 
    
                    for t in range(len(process_time)):
                        if task_test[i]['SG']==process_time[t]['SG'] and  lujing[lu_index][1]==process_time[t]['DEVICE_ID'] :
                            ttt=t
                fo.write(' '+str(process_time[ttt]['PROCESS_TIME']))
            elif j==2:
                m1=len(task_test[i]['FINERY_PATH_ID'].strip())
                
                for n in range(m1):
                    
                    
                    fo.write(task_test[i]['PONO']+' '+((task_test[i]['FINERY_PATH_ID']).strip())[int(n)])
                    ###更改的地方
                    if (task_test[i]['FINERY_PATH_ID']).strip()[int(n)]=='I':
                        lishi.remove('L')
                    else:
                        lishi.remove((task_test[i]['FINERY_PATH_ID'].strip())[n])
                    ###更改的地方
                    for o in range(lujing_x.shape[0]):
                        if lujing[o][0]==((task_test[i]['FINERY_PATH_ID']).strip())[int(n)]:
                            lu_index=o#zheli zh
                    for t in range(len(process_time)):
                        if task_test[i]['SG']==process_time[t]['SG'] and  lujing[lu_index][1]==process_time[t]['DEVICE_ID'] :
                            ttt=t
                    fo.write(' '+str(process_time[ttt]['PROCESS_TIME']))
                    
                    
                    
                    fo.write("\n")
                for n in range(3-m1):
                    fo.write(task_test[i]['PONO']+' '+lishi[n]+' '+str(0))
                    if n!=2-m1:
                        fo.write("\n")
            elif j==gongxushu-3:
                
                fo.write(task_test[i]['PONO']+' '+guxu_sy[gongxushu-1])
                for o in range(lujing_x.shape[0]):
                    #print(lujing_x)
                    if lujing[o][0]==guxu_sy[j+2]:
                        #print("O",o)
                        
                        lu_index=o#zheli zhi xuan ze yige 
                        #print("O",o,lu_index)
                        ####这是需要更改的 38
                    for t in range(len(process_time)):
                        if task_test[i]['SG']==process_time[t]['SG'] and  task_test[i]['CC_ID']==process_time[t]['DEVICE_ID'] :
                            
                           
                            tttttt=t
                 ###改的地方
                i_index=getTwoDimensionListIndex(cast_time,task_test[i]['PONO'])
                fo.write(' '+str(cast_time[i_index][1]))
            if i==lu-1 and j==gongxushu-3:
                fo.write(';') 
            else:
                fo.write("\n")
    

    time=[]
    gongxu_list=[]
    gongxu_zd={}
    for mm in guxu_sy:
        gongxu_list.append(mm)
    for nnn in gongxu_list:
        for oo in range(lujing_x.shape[0]): 
            if lujing[oo][0]==nnn:
               gongxu_zd[nnn] =lujing[oo][1]
               break;
    
                
    
    
    for i in range(len(transport_time)):
        if (transport_time[i]['START_ID']==str(gongxu_zd['D']) and transport_time[i]['END_ID']==str(gongxu_zd['B'])) or (transport_time[i]['START_ID']==str(gongxu_zd['B']) and transport_time[i]['END_ID']==str(gongxu_zd['R'])) or (transport_time[i]['START_ID']==str(gongxu_zd['R']) and transport_time[i]['END_ID']==str(gongxu_zd['L'])) or(transport_time[i]['START_ID']==str(gongxu_zd['L']) and transport_time[i]['END_ID']==str(gongxu_zd['U'])) or (transport_time[i]['START_ID']==str(gongxu_zd['U']) and transport_time[i]['END_ID']==str(gongxu_zd['T'])):
            time.append(transport_time[i]['TRANSTIME'])
          
    
    
    fo.write("\n")
    fo.write('param T:')
    fo.write("\n")
    fo.write('        ')
    for n in range(1,len(guxu_sy)):
        fo.write(guxu_sy[n]+'  ')
    fo.write(':=')
    
    fo.write("\n")
    
    for i in range(len(guxu_sy)-1):    
        fo.write('     ')
        fo.write(str(guxu_sy[i])+' ')
        for j in range(1,len(guxu_sy)):
            if i>=j:
                fo.write(str(0)+' ')
            else:
                for n in range(len(transport_time)):
                    if (gongxu_zd[guxu_sy[i]]==transport_time[n]['START_ID'] and gongxu_zd[guxu_sy[j]]==transport_time[n]['END_ID'])  :
                        fo.write(str(transport_time[n]['TRANSTIME'])+' ')
        if i==len(guxu_sy)-2:
            fo.write(';') 
        else:
            fo.write("\n")
    jiaoci_beigin_time=[]
    jiaoci_beigin_time1=predict_jiaoci_beigin_time(cast_time,list_CC_START_TIME,list_jiaoci_start,list_luci)
    for i in range(len(jiaoci_beigin_time1)):
        jiaoci_beigin_time.append(jiaoci_beigin_time1[i][1])
   
    #jiaoci_beigin_time=[200,506,200,316,400,500,200,392,546]

    fo.write("\n")
    fo.write('param :d:=')
    fo.write("\n")
    for i in range(len(jiaoci_beigin_time)):
        fo.write('   ')
        fo.write(str(jiaoci_begin[i]))
        fo.write(' ')
        fo.write(str(jiaoci_beigin_time[i]))
        if i==len(jiaoci_beigin_time)-1:
            fo.write(';') 
        else:
            fo.write("\n")
    fo.close() 
    return list_sb,cast_time

#预计浇次计算函数。输入cast_time是整理后的各个浇次时间，剩下的输入同上意思。输出就是各个浇次预计开浇时间集合
def predict_jiaoci_beigin_time(cast_time,list_CC_START_TIME,list_jiaoci_start,list_luci):
    
    def time_char_to_minute(timeDateStr):#时间转化成‘分’的函数
        time1=datetime.datetime.strptime(timeDateStr,"%Y-%m-%d %H:%M:%S")
        secondsFrom1970=time.mktime(time1.timetuple())
        ticks = time.time()
        time_result=(secondsFrom1970-ticks)/60
        time_result=float('%.2f' % time_result)
        return int(time_result)
    def getTwoDimensionListIndex(L,value): # 
     
        data = [data for data in L if data[0]==value]  
        index = L.index(data[0])  
        return index
    #做一个炉次的集合
    jiaoci_beigin_time=[[0 for i in range(2)]for i in range(len(list_jiaoci_start))]
    for i in range(len(list_jiaoci_start)):
        jiaoci_beigin_time[i][0]=list_jiaoci_start[i]
        
    num_cast_predict=0
    num_cast_plan=0
    sum_num=0
    list_CC_START_TIME.append(['0', '0'])
    for i in range(len(list_luci)):
        if list_luci[i]==list_CC_START_TIME[num_cast_predict][0]:
            sum_num=time_char_to_minute(list_CC_START_TIME[num_cast_predict][1])
            jiaoci_beigin_time[num_cast_plan][1]=time_char_to_minute(list_CC_START_TIME[num_cast_predict][1])
            num_cast_predict=num_cast_predict+1
            num_cast_plan=num_cast_plan+1
            index=getTwoDimensionListIndex(cast_time,list_luci[i])
            sum_num=sum_num+(cast_time[index][1])#时间累和
        elif list_luci[i]==list_jiaoci_start[num_cast_plan] and list_luci[i]!=list_CC_START_TIME[num_cast_predict][0]:
            index=getTwoDimensionListIndex(cast_time,list_luci[i])
            jiaoci_beigin_time[num_cast_plan][1]=sum_num+80
            sum_num=sum_num+(cast_time[index][1])+80#时间累和加80是因为换炉子的时间
            
            num_cast_plan=num_cast_plan+1
        else:
            index=getTwoDimensionListIndex(cast_time,list_luci[i])
            sum_num=sum_num+(cast_time[index][1])#时间累和
            
    return jiaoci_beigin_time 
#这部分是主函数，用于调用上诉所有函数，也是外部接口使用的时候所要调用的函数    
'''    
def schedule_steel(selected_tasks,process_time,code_device,transport_time):
    list_jiaoci_start, list_luci, list_jiaoci_end,list_remove_end,list_pono_cast,list_CC_ID,list_CC_START_TIME =task_pack(selected_tasks)
    task_inspect(selected_tasks,process_time,code_device,transport_time)
    task_test=selected_tasks
    #data/文件的写入
    list_sb,cast_time=data(task_test,process_time,code_device,transport_time,list_jiaoci_start, list_luci, list_jiaoci_end,list_remove_end,list_pono_cast,list_CC_ID,list_CC_START_TIME)
   
    jiaoci_beigin_time =predict_jiaoci_beigin_time(cast_time,list_CC_START_TIME,list_jiaoci_start,list_luci)

    #模型的计算
    model=model_main(list_sb,list_CC_ID,list_pono_cast)#调度模型  
    
    #模型的求解
    solver = SolverFactory("gurobi")    
    instance = model.create_instance('foo1.dat')
    #results = solver.solve(instance,tee=True,keepfiles=False)
    #results.write()
    #固定整数变量
    
    
    instance.x.fixed = True
    instance.y.fixed = True
    
    instance.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    
    results = solver.solve(instance,tee=True,keepfiles=False)
    results.write()
    

    #获取对偶变量
    print ("Duals")
    for c in instance.component_objects(Constraint, active=True):
        print ("   Constraint",c)
        for index in c:
            print ("      ", index, instance.dual[c[index]])

    
   
    
    #结果输出
    list_hang=[]
    list_lie=[]
    for i in instance.I:
        list_hang.append(i)
        
        for j in instance.J:
           
            for k in instance.K:
                
                if instance.x[i,j,k].value==1:
                    
                    list_hang.append(k)
                    list_hang.sort()
        list_lie.append(list_hang.copy())
        list_hang.clear()

    list_hang2=[]
    list_lie2=[]
    for i in instance.I:
        for j in instance.J:
            for k in instance.K:
               if instance.x[i,j,k].value==1:
                   list_hang2.append(i)
                   list_hang2.append(k)
                   list_hang2.append(instance.t[i,j].value)
                   list_lie2.append(list_hang2.copy())
                   list_hang2.clear()          
   
    #结果转化成字典
   
    list_result=result_list_to_result(task_test,process_time,list_lie,list_lie2,list_hang,cast_time)#
   
    
    return list_result
 '''
def schedule_steel(selected_tasks,process_time,code_device,transport_time):
    list_jiaoci_start, list_luci, list_jiaoci_end,list_remove_end,list_pono_cast,list_CC_ID,list_CC_START_TIME =task_pack(selected_tasks)
    task_inspect(selected_tasks,process_time,code_device,transport_time)
    task_test=selected_tasks
    #data/文件的写入
    list_sb,cast_time=data(task_test,process_time,code_device,transport_time,list_jiaoci_start, list_luci, list_jiaoci_end,list_remove_end,list_pono_cast,list_CC_ID,list_CC_START_TIME)
   
    jiaoci_beigin_time =predict_jiaoci_beigin_time(cast_time,list_CC_START_TIME,list_jiaoci_start,list_luci)

    #模型的计算
    model=model_main(list_sb,list_CC_ID,list_pono_cast)#调度模型  
    
    #模型的求解
    solver = SolverFactory("gurobi")    
    instance = model.create_instance('foo1.dat')
    results = solver.solve(instance,tee=True,keepfiles=False)
    results.write()
    instance.solutions.store_to(results)
    
   
    '''
    #固定整数变量   
    
    instance.x.fixed = True
    instance.y.fixed = True
    
    instance.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    
    solver1 = SolverFactory("ipopt")    

    results = solver1.solve(instance,tee=True,keepfiles=False)
    results.write()
    instance.solutions.store_to(results)

    
    i = 0
    for sol in results.solution:
        print("Solution "+str(i))
        #
        print(sorted(sol.variable.keys()))
        for var in sorted(sol.variable.keys()):
            print("  Variable "+str(var))
            print("    "+str(sol.variable[var]['Value']))
            #for key in sorted(sol.variable[var].keys()):
                #print('     '+str(key)+' '+str(sol.variable[var][key]))
        #
        for con in sorted(sol.constraint.keys()):
            print("  Constraint "+str(con))
            for key in sorted(sol.constraint[con].keys()):
                print('     '+str(key)+' '+str(sol.constraint[con][key]))
        #
        i += 1
    
    
    # An alternate way to print just the constraint duals
    print("")
    print("Dual Values")
    for con in sorted(results.solution(0).constraint.keys()):
        print(str(con)+' '+str(results.solution(0).constraint[con]["Dual"]))
    
    
    #获取对偶变量
    print ("Duals")
    for c in instance.component_objects(Constraint, active=True):
        #print ("   Constraint",c)
        for index in c:
            print ("      ", index, instance.dual[c[index]])
    '''
    
   
    
    #结果输出
    list_hang=[]
    list_lie=[]
    for i in instance.I:
        list_hang.append(i)
        
        for j in instance.J:
           
            for k in instance.K:
                
                if instance.x[i,j,k].value==1:
                    
                    list_hang.append(k)
                    list_hang.sort()
        list_lie.append(list_hang.copy())
        list_hang.clear()

    list_hang2=[]
    list_lie2=[]
    for i in instance.I:
        for j in instance.J:
            for k in instance.K:
               if instance.x[i,j,k].value==1:
                   list_hang2.append(i)
                   list_hang2.append(k)
                   list_hang2.append(instance.t[i,j].value)
                   list_lie2.append(list_hang2.copy())
                   list_hang2.clear()          
   
    #结果转化成字典
   
    list_result=result_list_to_result(task_test,process_time,list_lie,list_lie2,list_hang,cast_time)#
   
    
    return list_result 
