# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from scipy.interpolate import interp1d
from numba import jit
from scipy import stats
import math
import pandas as pd
plt.style.use('ggplot')
import matplotlib.cm as cm
import seaborn as sns
import csv
from pandas import Series, DataFrame
cm = plt.cm.get_cmap('RdYlBu')

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
  #  return 1

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

Placerefriend = {}
Placefriend = {}
Dict={}
Storage = {}
Revisitusernum = {}
visiternum = {}
Revisitfootstep = {}
Visitfootstep = {}
Avarevisitfreqcount = {}
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
                    Visitfootstep[place].append(person)
                    
            else:#这个地方的id头一次出现
                Dict[place]={person:translation}
                Storage[place]={person:[]}
                Revisitfootstep[place] = []
                Revisitusernum[place] = 0
                visiternum[place] = 1
                Visitfootstep[place] = [person]
                
        elif translation=='error':
            print(linestr)
f.close()      

print('开始计算频率')
for place in Revisitusernum:
        Avauserfreqcount[place] = Revisitusernum[place]/visiternum[place] #重访人数/总访问人数
        Avarevisitfreqcount[place] = Oldusercount[place]/Visitcount[place]#重访次数/总次数


Refriendcount={}
Friendcount={} #visit过得friend的数量
print('初始化Friendcount')
for place in Visitfootstep:
    Friendcount[place] = {}
    for person in Visitfootstep[place]:
        Friendcount[place][person] = 0
 
for place in Revisitfootstep:
    Refriendcount[place]={}
    for person in Revisitfootstep[place]:
        Refriendcount[place][person] = 0
        
Friendnumcount = {}
print('初始化Friendnumcount')
for place in Revisitfootstep.keys():
    for person in Revisitfootstep[place]:
        Friendnumcount[person] = 0
                
Frienddetail={}
Friendnewold = {}
Friendornot = {}
with open('I:/s/dataset_WWW2019/dataset_WWW_friendship_old.txt','r',encoding='utf-8') as f:
    print('好友关系开始')
    
    for line in f.readlines():
        linestr=line.strip()
        linstrlist=linestr.split('\x09')
        userId=linstrlist[0]
        friend=linstrlist[1]
        
#     

        if userId in Frienddetail:
            Frienddetail[userId].append(friend)
            Friendnewold[userId].append(friend)
        else:
            Frienddetail[userId] = [friend]
            Friendnewold[userId] = [friend]
            
        if friend in Frienddetail:
            Frienddetail[friend].append(userId)
            Friendnewold[friend].append(userId)
        else:
            Frienddetail[friend] = [userId]
            Friendnewold[friend] = [userId]
                    
#
                   
f.close()


#with open('I:/s/dataset_WWW2019/dataset_WWW_friendship_new.txt','r',encoding='utf-8') as f:
#    print('好友关系开始')
#    
#    for line in f.readlines():
#        linestr=line.strip()
#        linstrlist=linestr.split('\x09')
#        userId=linstrlist[0]
#        friend=linstrlist[1]
#        
#        if userId in Friendnewold.keys():
#            Friendornot[userId] = 0
#            for person in Friendnewold[userId]:
#                if person == friend:
#                    Friendornot[userId] = 0
#                    continue
#                else:
#                    Friendornot[userId] += 1
#        if friend in Friendnewold.keys():
#            Friendornot[friend] = 0
#            for person in Friendnewold[friend]:
#                if person == userId:
#                    Friendornot[friend] = 0
#                    continue
#                else:
#                    Friendornot[friend] += 1
##
#                   
#f.close()

with open('I:/s/dataset_WWW2019/dataset_WWW_friendship_new.txt','r',encoding='utf-8') as f:
    print('好友关系开始')
    
    for line in f.readlines():
        linestr=line.strip()
        linstrlist=linestr.split('\x09')
        userId=linstrlist[0]
        friend=linstrlist[1]
        
#     

        if userId in Frienddetail:
            Frienddetail[userId].append(friend)
        else:
            Frienddetail[userId] = [friend]
            
        if friend in Frienddetail:
            Frienddetail[friend].append(userId)
        else:
            Frienddetail[friend] = [userId]
                    
#
                   
f.close()

        
print('计算地区visit好友量')
for place in Visitfootstep:
    for person in Visitfootstep[place]: #for 这‘； OK，.个地方造访过的人
        if person in Frienddetail.keys(): #如果好友列表中有这个人
            for friend in Frienddetail[person]: #for 这个人的好友们
                if friend in Visitfootstep[place]: #如果这个人的好友也造访过这个地方
                    Friendcount[place][person] = Friendcount[place][person] + 1 #这个地方的这个人的好友关系+1个人
                    #print(Friendcount[place][person])
                else:
                    pass
                
print('计算地区的revisit好友量')
for place in Revisitfootstep:
    for person in Revisitfootstep[place]: #for 这个地方重访过的人
        if person in Frienddetail.keys(): #如果好友列表中有这个人
            for friend in Frienddetail[person]: #for 这个人的好友们
                if friend in Revisitfootstep[place]: #如果这个人的好友也重访过这个地方
                    Refriendcount[place][person] = Refriendcount[place][person] + 1 #这个地方的这个人的好友关系+1个人
                    #print(Friendcount[place][person])
                else:
                    pass
                
print('开始计算地区总visit好友量')
for place in Visitfootstep.keys():
    Placefriend[place] = 0
    for person in Visitfootstep[place]:
        if person in Friendcount[place]:
            Placefriend[place] = Placefriend[place] + Friendcount[place][person]
            #print(Placefriend[place])
        else:
            pass
        
print('开始计算地区总revisit好友量')
for place in Revisitfootstep.keys():
    Placerefriend[place] = 0
    for person in Revisitfootstep[place]:
        if person in Refriendcount[place]:
            Placerefriend[place] = Placerefriend[place] + Refriendcount[place][person]
            #print(Placefriend[place])
        else:
            pass

print('计算总visit和revisit的好友关系量与总revisit和visit人数')
total_friend = 0
total_visiter = 0
total_refriend = 0
total_revisiter = 0
for place in Placefriend:
    if place in visiternum:
        total_friend = total_friend + Placefriend[place]
        total_visiter = total_visiter + visiternum[place]
        
for place in Placerefriend:
    if place in Revisitusernum:
        total_refriend = total_refriend + Placerefriend[place]
        total_revisiter = total_revisiter + Revisitusernum[place]
        
        
Avafriend = {}
Logfriend = {}
Avarefriend = {}
Logrefriend = {}
print('计算visit关系量')
for place in Revisitusernum.keys():
    #print(visiternum[place])
    if place in visiternum.keys():
        if visiternum[place] == 1:
            Avafriend[place] = 0
        else:
            Avafriend[place] = Placefriend[place] / ((visiternum[place] * (visiternum[place]-1))/2)

            if Placefriend[place] == 0:
                pass
            else:
                Logfriend[place] = math.log10(Avafriend[place])#Placefriend[place])
            
print('计算revisit关系量')
for place in Revisitusernum.keys():
    if Revisitusernum[place] == 0 or Revisitusernum[place] == 1:
        Avarefriend[place] = 0
    else:
        Avarefriend[place] = Placerefriend[place] / ((Revisitusernum[place] * (Revisitusernum[place]-1))/2)
        
        if Placerefriend[place] == 0:
                pass
        else:
            Logrefriend[place] = math.log10(Avarefriend[place])#Placefriend[place])
            #print(Avafriend[place])
            
print('开始写入平均好友量')
with open('I:/s/2019firendresult.txt','w',encoding='utf-8') as file:#labels写入工作,以便储存
    for key,value in Avauserfreqcount.items():
        #print(i)
        file.write(str(key))
        file.write("                          ")
        file.write(str(value))
        file.write("\n")
file.close()

print('绘制未降噪散点图')
print('此为访问用户的人数频率vs好友关系 （未降噪效果图）')
x = []
y = []
temp = {'place': [], 'LogF':[], 'userF':[]}
for place in Avauserfreqcount:
    if place in Logfriend:
        temp['place'].append(place)
        temp['LogF'].append(Avafriend[place])
        temp['userF'].append(Avauserfreqcount[place])
        y.append(Avafriend[place])
        x.append(Avauserfreqcount[place])

temp = DataFrame(temp, index = temp['LogF'])
sns.pointplot(x='userF', y='LogF', data=temp, color='purple')
plt.show()
plt.scatter(x, y, alpha=0.11, color='purple')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('Percentage of revisited user vs Friendship density')
plt.xlabel('Percentage of revisited user')
plt.ylabel('Friendship density')
plt.show()

hexbin = sns.jointplot(x = temp['userF'], y = temp['LogF'], kind='hex',color='purple')
hexbin.set_axis_labels('Percentage of visited user', 'Friend density')
plt.show()
density = sns.kdeplot(temp['userF'],temp['LogF'], shade=True, color='purple')
plt.show()
#
#
#coefficient3 = stats.pearsonr(x,y)
#print(coefficient3)

#print('此为重访次数频率vs好友关系 （未降噪效果图）')
#x = []
#y = []
#for place in Avarevisitfreqcount:
#    if place in Logfriend:     
#        y.append(Logfriend[place])
#        x.append(Avarevisitfreqcount[place])
#    
#plt.scatter(x, y, alpha=0.11, color='red')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
#plt.title('Percentage of revisited count vs Friendship density(log)')
#plt.xlabel('Percentage of revisited count')
#plt.ylabel('Friendship density(log)')
#plt.show()
#
#coefficient4 = stats.pearsonr(x,y)
#print(coefficient4)

print('绘制降噪后的散点图')
x = []
y = []
for place in Avauserfreqcount:
    if place in Avafriend:
        if visiternum[place] >= 30 and Avafriend[place] >= 0.1:
            y.append(Avafriend[place])
            x.append(Avauserfreqcount[place])
    
plt.scatter(x, y, alpha=0.2, color='blue')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('Place revisited user count frequency vs Place friend relationship')
plt.xlabel('Revisited user frequency')
plt.ylabel('friend')
plt.show()
coefficient1 = stats.pearsonr(x,y)
print(coefficient1)

x = []
y = []
for place in Avauserfreqcount:
    if place in Avafriend:
        if visiternum[place] >= 25 and Avafriend[place] >= 0.1 and Avarevisitfreqcount[place] != 0:
            y.append(Avafriend[place])
            x.append(Avarevisitfreqcount[place])
    
plt.scatter(x, y, alpha=0.2, color='red')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('Place revisit times count frequency vs Place friend relationship')
plt.xlabel('Revisit frequency')
plt.ylabel('friend')
plt.show()

coefficient2 = stats.pearsonr(x,y)
print(coefficient2)
print('开始绘制重访用户数量的频率vs好友关系的图')
x = []
y = []
a = []
d = []
e = []
r = []
u = []
i = []
for place in Avauserfreqcount:
    if place in Logfriend:
            
        if visiternum[place] > 0 and visiternum[place] <= 200:
            y.append(Logfriend[place])
            x.append(Avauserfreqcount[place])
        elif visiternum[place] > 200 and visiternum[place] <= 400:
            a.append(Logfriend[place])
            d.append(Avauserfreqcount[place])
        elif visiternum[place] > 400 and visiternum[place] <= 600:
            e.append(Logfriend[place])
            r.append(Avauserfreqcount[place])
        elif visiternum[place] > 600:
            u.append(Logfriend[place])
            i.append(Avauserfreqcount[place])


plt.scatter(x, y, alpha=0.11, color='purple')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('0-200 Percentage of revisited user vs Friend density(log)')
plt.xlabel('Percentage of revisited user')
plt.ylabel('Friendship density(log)')
plt.show()
plt.scatter(d, a, alpha=0.11, color='purple')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('200-400 Percentage of revisited user vs Friend density(log)')
plt.xlabel('Percentage of revisited user')
plt.ylabel('Friendship density(log)')
plt.show()
plt.scatter(r, e, alpha=0.11, color='purple')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('400-600 Percentage of revisited user vs Friend density(log)')
plt.xlabel('Percentage of revisited user')
plt.ylabel('Friendship density(log)')
plt.show()
plt.scatter(i, u, alpha=0.11, color='purple')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('600- Percentage of revisited user vs Friend density(log)')
plt.xlabel('Percentage of revisited user')
plt.ylabel('Friendship density(log)')
plt.show()
#
#coefficient3 = stats.pearsonr(x,y)
#print(coefficient3)

print('绘制六边形图与密度图')
tempDict = {'place':[], 'Avafreq': [], 'friend':[]}
tempDict1 = {'place':[], 'Avafreq': [], 'friend':[]}
tempDict2 = {'place':[], 'Avafreq': [], 'friend':[]}
tempDict3 = {'place':[], 'Avafreq': [], 'friend':[]}
print('制作符合pandas要求的DataFrame')
for place in Avauserfreqcount:
    if place in Logfriend:
        tempDict['place'].append(place)
        if visiternum[place] > 0 and visiternum[place] <= 200:
            tempDict['Avafreq'].append(Avauserfreqcount[place])
            tempDict['friend'].append(Logfriend[place])
            
        elif visiternum[place] > 200 and visiternum[place] <= 400:
            tempDict1['Avafreq'].append(Avauserfreqcount[place])
            tempDict1['friend'].append(Logfriend[place])
            
        elif visiternum[place] > 400 and visiternum[place] <= 600:
            tempDict2['Avafreq'].append(Avauserfreqcount[place])
            tempDict2['friend'].append(Logfriend[place])
            
        elif visiternum[place] > 600:
            tempDict3['Avafreq'].append(Avauserfreqcount[place])
            tempDict3['friend'].append(Logfriend[place])
#tempdf = DataFrame(tempDict, index = tempDict['friend'])
#tempdf.plot.hexbin(x='Avafreq',y='friend', gridsize=10)
#sns.pointplot(x = tempDict['Avafreq'], y = tempDict['friend'],data=tempdf, ci=68)
hexbin = sns.jointplot(x = tempDict['Avafreq'], y = tempDict['friend'], kind='hex',color='purple')
hexbin.set_axis_labels('Percentage of revisited user', 'Friend density(log)')
plt.show()
density = sns.kdeplot(tempDict['Avafreq'],tempDict['friend'], shade=True, color='purple')
plt.show()

hexbin1 = sns.jointplot(x = tempDict1['Avafreq'], y = tempDict1['friend'], kind='hex',color='purple')
hexbin1.set_axis_labels('Percentage of revisited user', 'Friend density(log)')
plt.show()
density1 = sns.kdeplot(tempDict1['Avafreq'],tempDict1['friend'], shade=True, color='purple')
plt.show()

hexbin2 = sns.jointplot(x = tempDict2['Avafreq'], y = tempDict2['friend'], kind='hex',color='purple')
hexbin2.set_axis_labels('Percentage of revisited user', 'Friend density(log)')
plt.show()
density2 = sns.kdeplot(tempDict2['Avafreq'],tempDict2['friend'], shade=True, color='purple')
plt.show()

hexbin3 = sns.jointplot(x = tempDict3['Avafreq'], y = tempDict3['friend'], kind='hex',color='purple')
hexbin3.set_axis_labels('Percentage of revisited user', 'Friend density(log)')
plt.show()
density3 = sns.kdeplot(tempDict3['Avafreq'],tempDict3['friend'], shade=True, color='purple')
plt.show()

print(total_friend / total_visiter)
print(total_refriend / total_revisiter)

objects = ('visiter friendship percentage', 'revisiter friendship percentage')
y_pos = np.arange(len(objects))
performance = [total_friend / total_visiter, total_refriend / total_revisiter]

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('percentage')
plt.title('visiter friendship vs revisiter friendship')
print('开始绘制重访次数频率vs好友关系的图')
x = []
y = []
for place in Avarevisitfreqcount:
    if place in Logfriend:
        if visiternum[place] >= 60 and Avarevisitfreqcount[place] != 0:#and Logfriend[place] >= 2 and Avarevisitfreqcount[place] != 0:
            y.append(Logfriend[place])
            x.append(Avarevisitfreqcount[place])
    
plt.scatter(x, y, alpha=0.11, color='red')  # 绘制散点图，透明度为0.6（这样颜色浅一点，比较好看）
plt.title('Percentage of revisited count vs Friend density(log)')
plt.xlabel('Percentage of revisited count')
plt.ylabel('Friendship density(log)')
plt.show()

coefficient4 = stats.pearsonr(x,y)
print(coefficient4)

print('绘制六边形图与密度图')
tempDict1 = {'place':[], 'Avatimefreq': [], 'friend':[]}
print('制作符合pandas要求的另一个DataFrame')
for place in Avarevisitfreqcount:
    if place in Logfriend:
        tempDict1['place'].append(place)
        if visiternum[place] >= 60 and Avarevisitfreqcount[place] != 0:
            tempDict1['Avatimefreq'].append(Avarevisitfreqcount[place])
            tempDict1['friend'].append(Logfriend[place])
        

#tempdf = DataFrame(tempDict, index = tempDict['friend'])
#tempdf.plot.hexbin(x='Avafreq',y='friend', gridsize=10)
hexbin2 = sns.jointplot(x = tempDict1['Avatimefreq'], y = tempDict1['friend'], kind='hex',color='red')
hexbin2.set_axis_labels('Percentage of revisited count','Friend density(log)')
plt.show()
hexbin3 = sns.kdeplot(tempDict1['Avatimefreq'],tempDict1['friend'], shade=True, color='red')
#hexbin3.set_axis_labels('Percentage of revisited count','Friend density(log)')
plt.show()

print('结束')
