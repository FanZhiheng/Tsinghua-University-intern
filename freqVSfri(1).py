# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.interpolate import interp1d
from numba import jit

def month(number,year):
    if year=='2013':
        if number=='Jan':
            return 0
        elif number=='Feb':
            return 31
        elif number=='Mar':
            return 31+28
        elif number=='Apr':
            return 31+28+31
        elif number=='May':
            return 31+28+31+30
        elif number=='Jun':
            return 31+28+31+30+31
        elif number=='Jul':
            return 31+28+31+30+31+30
        elif number=='Aug':
            return 31+28+31+30+31+30+31
        elif number=='Sep':
            return 31+28+31+30+31+30+31+31
        elif number=='Oct':
            return 31+28+31+30+31+30+31+31+30
        elif number=='Nov':
            return 31+28+31+30+31+30+31+31+30+31
        else:
            return 31+28+31+30+31+30+31+31+30+31+30
    else:
        if number=='Jan':
            return 0
        elif number=='Feb':
            return 31
        elif number=='Mar':
            return 31+29
        elif number=='Apr':
            return 31+29+31
        elif number=='May':
            return 31+29+31+30
        elif number=='Jun':
            return 31+29+31+30+31
        elif number=='Jul':
            return 31+29+31+30+31+30
        elif number=='Aug':
            return 31+29+31+30+31+30+31
        elif number=='Sep':
            return 31+29+31+30+31+30+31+31
        elif number=='Oct':
            return 31+29+31+30+31+30+31+31+30
        elif number=='Nov':
            return 31+29+31+30+31+30+31+31+30+31
        else:
            return 31+29+31+30+31+30+31+31+30+31+30

def judge(year):
    if year=='2013':
        return 1
    else:
        return 0

def translate(d):
    trans=d.split(' ')
    if len(trans)>=5:
        year=trans[5]
        mon=trans[1]
        day=trans[2]
        time=trans[3].split(':')
        return judge(year)*366*24*3600+int(month(mon,year))*24*3600+int(day)*24*3600+int(time[0])*3600+int(time[1])*60+int(time[2])
    else:
        return 'error'

def time_class(time,divider):
    if time<=divider[0]:
        return 0
    for i in range(1,len(divider)):
        if time>=divider[i-1] and time<=divider[i]:
            return i
    return len(divider)


##venuelist=["Colleges & Universities","Great Outdoors","Shop & Service","Arts & Entertainment","Food","Travel & Transport","Nightlife Spots","Residence","Professional & Other Places"]
#VenueDict={}
#Venuelist=[] #地点类型
#Venuehash={}
#m=0
#with open('E:/s/dataset_TIST2015_POIs.txt','r',encoding='utf-8') as file:#Venue相关信息记录
#    for line in file.readlines():
#        linestr=line.strip()
#        linstrlist=linestr.split('\x09')
#        place=linstrlist[0]
#        venue=linstrlist[3]
#        VenueDict[place]={'Venue':venue}
#        if venue in Venuelist:
#            continue
#        else:
#            Venuelist.append(venue)
#            Venuehash[venue]=m
#            m=m+1
#file.close()
#
#print('finish1')

Visitcount={}#进行预处理相关的数据统计，以便筛下去总visit数<5的PoI和User
Uservisitcount={}
Oldusercount = {} #记录这个user是不是已经去过的人
Avauserfreqcount = {}
Avarevisitfreqcount = {}
with open('I:/s/dataset_WWW2019/dataset_WWW_Checkins_anonymized.txt','r',encoding='utf-8') as f:
    print('开始玩')
    for line in f.readlines():
        linestr=line.strip()
        linstrlist=linestr.split('\x09')
        person=linstrlist[0]
        place=linstrlist[1]
        if place in Visitcount:
            Visitcount[place]=Visitcount[place]+1
        else:
            Visitcount[place]=1
        if person in Uservisitcount:
            Uservisitcount[person]=Uservisitcount[person]+1
        else:
            Uservisitcount[person]=1

f.close()

Dict={}
Storage={}
Venue={}
timelist=[3600,14400,43200,86400,122188,172800,256291,353390,491183,604800,854360,1209600,1814400,2592000,5184000]
with open('I:/s/dataset_WWW2019/dataset_WWW_Checkins_anonymized.txt','r',encoding='utf-8') as f:
    print('时间筛选开始')
    for line in f.readlines():
        
        linestr=line.strip()
        linstrlist=linestr.split('\x09')#listrlist[2]是时间，格式为2010-03-05 16:38:48 linstrlist[0]为用户，linstrlist[1]为地点
        translation=translate(linstrlist[2])
        place=linstrlist[1]
        person=linstrlist[0]
        if Visitcount[place]>=5 and Uservisitcount[person]>=5 and translation!='error':
            if person in Dict:#Dict存每个人每个地点的最后访问时间，Storage存每个人全部的Revisitation时间间隔信息->person和place位置对调,venue存该人的访问信息
                if place in Dict[person]:#第二次被来
                    deltat=translation-Dict[person][place]
                    Dict[person][place]=translation
                    if deltat>60*30:
                        Storage[person][place].append(time_class(deltat,timelist))
                        Oldusercount[place] = Oldusercount[place] + 1
                        
                    
                else:
                    Dict[person][place]=translation
                    Storage[person][place]=[]
                    Oldusercount[place] = 0
                    
                    
            else:#头一次来
                Dict[person]={place:translation}
                Storage[person]={place:[]}
                Oldusercount[place] = 0
                
        elif translation=='error':
            print(linestr)
f.close()      

Placefriend = {}
Dict={}
Storage = {}
Revisitusernum = {}
visiternum = {}
Revisitfootstep = {}
with open('I:/s/dataset_WWW2019/dataset_WWW_Checkins_anonymized.txt','r',encoding='utf-8') as f:
    print('时间筛选开始')
    for line in f.readlines():
        
        linestr=line.strip()
        linstrlist=linestr.split('\x09')#listrlist[2]是时间，格式为2010-03-05 16:38:48 linstrlist[0]为用户，linstrlist[1]为地点
        translation=translate(linstrlist[2])
        place=linstrlist[1]
        person=linstrlist[0]
        if Visitcount[place]>=5 and Uservisitcount[person]>=5 and translation!='error':
            if place in Dict:#Dict存每个人每个地点的最后访问时间，Storage存每个人全部的Revisitation时间间隔信息->person和place位置对调,venue存该人的访问信息
                if person in Dict[place]:#这里讲revisit
                    deltat=translation-Dict[place][person]
                    Dict[place][person]=translation
                    if deltat>60*30:
                        Storage[place][person].append(time_class(deltat,timelist))
                        if person in Revisitfootstep[place]:
                            pass
                        else:
                            Revisitusernum[place] = Revisitusernum[place] + 1
                            Revisitfootstep[place].append(person)
                        
                    
                else: #这里讲newuser
                    Dict[place][person]=translation
                    Storage[place][person]=[]
                    visiternum[place] = visiternum[place] + 1
                    
                    
            else:#这个地方的id头一次出现
                Dict[place]={person:translation}
                Storage[place]={person:[]}
                Revisitfootstep[place] = []
                Revisitusernum[place] = 0
                visiternum[place] = 1
                
        elif translation=='error':
            print(linestr)
f.close()      

print('开始计算频率')
for place in Revisitusernum:
        Avauserfreqcount[place] = Revisitusernum[place]/visiternum[place] #重访人数/总访问人数
        Avarevisitfreqcount[place] = Oldusercount[place]/Visitcount[place]
        

print('开始写入')
with open('I:/s/2019result.txt','w',encoding='utf-8') as file:#labels写入工作,以便储存
    for key,value in Avauserfreqcount.items():
        #print(i)
        file.write(str(key))
        file.write("                          ")
        file.write(str(value))
        file.write("\n")
file.close()


Friendcount={}
print('初始化Friendcount')
for place in Revisitfootstep.keys():
    for person in Revisitfootstep[place]:
        Friendcount[person] = 0
 
                
Frienddetail={}
with open('I:/s/dataset_WWW2019/dataset_WWW_friendship_new.txt','r',encoding='utf-8') as f:
    print('好友关系开始')
    
    for line in f.readlines():
        linestr=line.strip()
        linstrlist=linestr.split('\x09')
        userId=linstrlist[0]
        friend=linstrlist[1]
        
        if userId in Friendcount:   
            Friendcount[userId] = Friendcount[userId] + 1
        elif friend in Friendcount:
            Friendcount[friend] = Friendcount[friend] + 1

                    
#        if userId in Frienddetail:
#            Frienddetail[userId] = Frienddetail[userId] + 1
#        elif:
#            Frienddetail[userId] = 1
                   
f.close()

print('开始计算地区总好友量')
for place in Revisitfootstep.keys():
    Placefriend[place] = 0
    for person in Revisitfootstep[place]:
        if person in Friendcount:
            Placefriend[place] = Placefriend[place] + Friendcount[person]
        else:
            pass
        
Avafriend = {}
print('开始计算平均好友量')
for place in Revisitusernum:
    if Revisitusernum[place] != 0:
        Avafriend[place] = Placefriend[place] / Revisitusernum[place]
    else:
        Avafriend[place] = 0
    
print('开始写入平均好友量')
with open('I:/s/2019firendresult.txt','w',encoding='utf-8') as file:#labels写入工作,以便储存
    for key,value in Avafriend.items():
        #print(i)
        file.write(str(key))
        file.write("                          ")
        file.write(str(value))
        file.write("\n")
file.close()

print('绘制散点图')
x = []
y = []
for place in Avauserfreqcount:
    if place in Avafriend:
        if Avafriend[place] >= 50 and Avafriend[place] <= 600 and visiternum[place] >= 10:
            y.append(Avafriend[place])
            x.append(Avauserfreqcount[place])
    
plt.scatter(x, y, alpha=0.6)  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('Place frequency vs Place average friend')
plt.xlabel('frequency')
plt.ylabel('friend')
plt.show()

print('结束')
