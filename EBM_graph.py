import pandas as pd
import numpy as np
import time
import string
import math
import matplotlib.pyplot as plt
import os
os.chdir('/Users/lvvv/Project')
import networkx as nx
from multiprocessing import Process
from copy import deepcopy
from EBM_funcation import *
from EBM_analysis import *

t=time.clock()
#train_data=pd.read_csv('/Users/lvvv/Project/references/data/dataset_TSMC2014_NYC.csv')
train_data=pd.read_csv('/Users/lvvv/Project/references/data/dataset_TSMC2014_TKY.csv')
s=[]
for i in range(len(train_data['utcTimestamp'])):
    s.append(time.mktime(time.strptime(train_data['utcTimestamp'][i].replace('+0000 ',''),"%a %b %d %H:%M:%S %Y"))+train_data['timezoneOffset'][i]*60)
train_data['time']=s

#筛选过后index不是连续的，使用reset_index(drop=True)来恢复
train_data=train_data[train_data.venueId.isin(list(venue_choice(train_data).index))].reset_index(drop=True)
venue=train_data['venueId'].value_counts()

#删除目前不需要的列
del train_data['venueCategoryId']
del train_data['latitude']
del train_data['longitude']
del train_data['timezoneOffset']
del train_data['utcTimestamp']

#从原始数据中产生所需要的边表
def get_csv(i):
    train_data=pd.DataFrame(np.load("TKYtraindata.npy"))
    train_data.columns = ['userId', 'venueId', 'venueCategory','time']
    G=main(train_data,i)
    for j in [0.6825,0.683,0.6835]:
        G_friend=nx.Graph()
        for k in G.edges():
            G_degree=nx.degree(G)
            if G[k[0]][k[1]]['strength']>j and G_degree[k[0]]>1 and G_degree[k[1]]>1:
                G_friend.add_weighted_edges_from([(k[0],k[1],G[k[0]][k[1]]['strength'])])
        export_edge_list(G_friend,filename="TKYedges"+"_"+str(j)+"_"+str(i)+".csv")

#把产生边表和分析数据过程合并
def linked(i):
    get_csv(i)
    analysis_max(i)

#六进程并发，加快运行速度
def mul_process_max():
	print("Parent process %s."%(os.getpid()))
	for i in range(6):
		#创建进程
		p = Process(target=linked,args=(600*i+600,))
		print("Process will start.")
		p.start()
	p.join()
	print("Process end")
