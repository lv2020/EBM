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

t=time.clock()
train_data=pd.read_csv('/Users/lvvv/Project/references/data/dataset_TSMC2014_NYC.csv')
#train_data=pd.read_csv('/Users/lvvv/Project/references/data/dataset_TSMC2014_TKY.csv')
s=[]
for i in range(len(train_data['utcTimestamp'])):
    s.append(time.mktime(time.strptime(train_data['utcTimestamp'][i].replace('+0000 ',''),"%a %b %d %H:%M:%S %Y"))+train_data['timezoneOffset'][i]*60)
train_data['time']=s

#筛选过后index不是连续的，使用reset_index(drop=True)来恢复
train_data=train_data[train_data.venueId.isin(list(venue_choice(train_data).index))].reset_index(drop=True)
venue=train_data['venueId'].value_counts()

#删除目前不需要的列
del train_data['venueCategoryId']
del train_data['venueCategory']
del train_data['latitude']
del train_data['longitude']
del train_data['timezoneOffset']
del train_data['utcTimestamp']

G = nx.Graph()
t1=time.clock()
G=co_occurrence(train_data,G)
print("计算co-occurrence vector用时为：",time.clock()-t1)

t1=time.clock()
D=diversity(G)
print("计算diversity用时为：",time.clock()-t1)

t1=time.clock()
LE=location_entropy(train_data)
print("计算location entropy用时为：",time.clock()-t1) 

t1=time.clock()
G=frequency(G,LE)
print("计算frequency用时为：",time.clock()-t1)

t1=time.clock()
G=socail_strength(G)
print("计算socail strength用时为：",time.clock()-t1)
print("总用时为：",time.clock()-t)

G_friend=nx.Graph()
for i in G.edges():
    if G[i[0]][i[1]]['strength']>0.642:
        G_friend.add_weighted_edges_from([(i[0],i[1],G[i[0]][i[1]]['strength'])])
drawGraph(G_friend)


