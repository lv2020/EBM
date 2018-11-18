import pandas as pd
import numpy as np
import time
import string
import math
import matplotlib.pyplot as plt
import os
import tkinter.messagebox
import networkx as nx
from copy import deepcopy
os.chdir('/Users/lvvv/Project')
from numpy import *
from EBM_funcation import *
from tkinter import *

#筛选数据
def venue_choice(train_data):
    venue=train_data['venueId'].value_counts()
    venue=venue[venue>1]
    c=np.zeros((3,len(venue.index)))
    a=list(venue.index)
    train_data=train_data[train_data.venueId.isin(a)].reset_index(drop=True)
    for i in range(len(train_data['userId'])):
        j=a.index(train_data['venueId'][i])
        c[0][j]=c[1][j]
        c[1][j]=train_data['userId'][i]
        if c[0][j]!=0 and c[0][j]!=c[1][j]:#不止出现一次并且前后两次用户Id不同
            c[2][j]=1
    return venue[c[2,:]>0]

#计算co-occurrence
def co_occurrence(train_data1,G):
    from copy import deepcopy
    user_list=list(train_data1['userId'].value_counts().index)
    venue=dict.fromkeys(train_data1['venueId'].value_counts().index, 0)
    count=0
    for i in range(len(train_data1['userId'])-1):
        #前后时间
        t=train_data1['time'][i]
        t1=train_data1['time'][i+1]
        #前后用户id
        num1=train_data1['userId'][i]
        num2=train_data1['userId'][i+1]
        #大于规定时间间隔
        if t1-t>3600:
            continue
        #处于同一地点且用户id不同
        if num1!=num2 and train_data1['venueId'][i]==train_data1['venueId'][i+1]:
            if (num1,num2) in G.edges():
                G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
                count+=1
            else:
                G.add_edge(num1,num2,weight=deepcopy(venue))#防止同时更改浅对象
                G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
                count+=1
            j=i-1
            while j>=0:
                num1=train_data1['userId'][j]
                t2=train_data1['time'][j]
                if t1-t2>3600:
                    break
                if num1!=num2 and train_data1['venueId'][j]==train_data1['venueId'][i+1]:
                    if (num1,num2) in G.edges():
                        G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
                        count+=1
                    else:
                        G.add_edge(num1,num2,weight=deepcopy(venue))#防止同时更改浅对象
                        G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
                        count+=1
                j=j-1
    print(count)
    return G

#计算location entropy
def location_entropy(train_data1):
    check_in_count=train_data1['venueId'].value_counts()
    userId=train_data1['userId'].value_counts()
    LE=[]
    for i in range(len(check_in_count)):
        #处于地点i的用户打卡次数
        new_data=train_data1[train_data1['venueId']==check_in_count.index[i]]['userId'].value_counts()
        #计算location entropy
        LE.append(-1*sum([m/sum(new_data)*math.log(m/sum(new_data)) for m in new_data if m!=0]))
    return LE

#计算diversity
def diversity(G):
    e=(1/(-0.9))
    for i in G.edges():
        co_sum=sum(list(G[i[0]][i[1]]['weight'].values()))
        G[i[0]][i[1]]['diversity']=0
        for j in G[i[0]][i[1]]['weight'].values():
            G[i[0]][i[1]]['diversity']+=(j/co_sum)**0.1
        G[i[0]][i[1]]['diversity']=G[i[0]][i[1]]['diversity']**e
    return G

#计算frequency
def frequency(G,LE):
    LE=np.exp(-mat(LE))
    for i in G.edges():
        G[i[0]][i[1]]['frequency']=(mat(list(G[i[0]][i[1]]['weight'].values()))*LE.T)[0,0]
    return G

#计算socail strength
def socail_strength(G):
    a=0.483
    b=0.520
    c=0.2
    for i in G.edges():
        G[i[0]][i[1]]['strength']=a*G[i[0]][i[1]]['diversity']+b*G[i[0]][i[1]]['frequency']+c
    return G

#画图
def drawGraph(fg, title='weighted_graph'):
    pos = nx.spring_layout(fg)
    nx.draw_networkx_nodes(fg, pos, node_shape='.', node_size=12)
    nx.draw_networkx_edges(fg, pos)
    nx.draw_networkx_labels(fg, pos,font_size=4)
    plt.savefig('1.png',dpi=300)
    plt.show()
