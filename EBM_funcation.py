import pandas as pd
import numpy as np
import time,datetime
import string
import math
import matplotlib.pyplot as plt
import os
import networkx as nx
from copy import deepcopy
os.chdir('/Users/lvvv/Project')

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

#了解随时间分布情况，预处理使用
def time_div(train_data):
    l=[]
    for i in range(3000):
        if min(s)+3600*24*i>max(s):
            break
        t=(s>min(s)+3600*24*i)&(s<min(s)+3600*24*(i+1))
        l.append(len(t[t==True]))
    x=range(len(l))
    plt.plot(x,l,marker='o',ms=3)
    plt.savefig('num_date_new.png', dpi=300)

#计算co-occurrence 和time
def co_occurrence(train_data1,G,timescale):
    from copy import deepcopy
    user_list=list(train_data1['userId'].value_counts().index)
    venue=dict.fromkeys(train_data1['venueId'].value_counts().index, 0)
    #记录不同venue的co-occurence时间的数组
    venueCategory=list(train_data1['venueCategory'].value_counts().index)
    venue_time=dict(zip(venueCategory,[[] for i in range(len(venueCategory))]))


    for i in range(len(train_data1['userId'])-1):
        #前后时间
        t=train_data1['time'][i]
        t1=train_data1['time'][i+1]
        #前后用户id
        num1=train_data1['userId'][i]
        num2=train_data1['userId'][i+1]
        #大于规定时间间隔
        if t1-t>timescale:
            continue
        #处于同一地点且用户id不同
        if num1!=num2 and train_data1['venueId'][i]==train_data1['venueId'][i+1]:
            VCI=train_data1['venueCategory'][i]
            venue_time[VCI].append(t)
            venue_time[VCI].append(t1)

            if (num1,num2) in G.edges():
                G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
            else:
                G.add_edge(num1,num2,weight=deepcopy(venue))#防止同时更改浅对象
                G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
            j=i-1
            while j>=0:
                num1=train_data1['userId'][j]
                t2=train_data1['time'][j]
                if t1-t2>timescale:
                    break
                if num1!=num2 and train_data1['venueId'][j]==train_data1['venueId'][i+1]:
                    venue_time[VCI].append(t2)
                    if (num1,num2) in G.edges():
                        G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
                    else:
                        G.add_edge(num1,num2,weight=deepcopy(venue))#防止同时更改浅对象
                        G[num1][num2]['weight'][train_data1['venueId'][i]]+=1
                j=j-1
    return G,venue_time

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

#gephi，输出边表
def export_edge_list(G, labels=None, filename="edges.csv", delim=",", header=True):
    f=open(filename,'w')
    f.close()
    f = open(filename, 'w')
    if header:
        f.write("Source,Target,Weight,Type\n")
    for i,j,w in G.edges(data=True):
        f.write(str(i)+delim+str(j)+delim+str(w['weight'])+delim+"undirected"+"\n")                         
    f.close()

#划分不同venue的时间分布，需要先调用co_occurrence 函数获得VCI
def venue_time_draw(VCI,timescale):
    l=[]
    VCI=pd.Series(VCI)
    for i in VCI.index:
        if(VCI[i]==[]):
            l.append(False)
        else:
            l.append(True)
    a=VCI[l]
    plt.rcParams['figure.figsize']=(9,13)
    for i,k in enumerate(a):
        for j in k:
            plt.scatter((j%(24*3600)/3600+8)%24,i,c='b',s=2,alpha=0.3)
    plt.yticks(range(len(a.index)),list(a.index))
    plt.yticks(fontsize=10)
    plt.xticks(fontsize=16)
    plt.title('TKY_co-occurence_timescale_'+str(timescale), fontsize=24)
    plt.savefig('TKY_co-occurence_timescale_'+str(timescale)+'.png',dpi=300,bbox_inches="tight")
    plt.clf()

#主体函数
def main(train_data,timescale):
    t=time.clock()
    G = nx.Graph()
    t1=time.clock()
    G,VCI=co_occurrence(train_data,G,timescale)
    print("计算co-occurrence vector用时为：",time.clock()-t1)
    
    #划分不同venue的时间分布
    venue_time_draw(VCI,timescale)
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
    
    l=[]
    for i in G.edges():
        l.append(G[i[0]][i[1]]['strength'])
    print("------------timescale:",timescale,"--------------")
    print("最大值为：",max(l))
    print("平均值为：",sum(l)/len(l))
    print("最小值为：",min(l))
    print("-------------------------------------------------")
    #plt.scatter(pd.value_counts(l).index,pd.value_counts(l))
    #plt.savefig('TKY_div_'+str(timescale)+'.png')
    return G
#输出不同参数的边表，便于下一步的分析
def cal(i):
    train_data=pd.DataFrame(np.load("TKYtraindata.npy"))
    train_data.columns = ['userId', 'venueId', 'venueCategory','time']
    G=main(train_data,i)
    for j in [0.682,0.684,0.686,0.688]:
        G_friend=nx.Graph()
        for k in G.edges():
            G_degree=nx.degree(G)
            if G[k[0]][k[1]]['strength']>j and G_degree[k[0]]>1 and G_degree[k[1]]>1:
                G_friend.add_weighted_edges_from([(k[0],k[1],G[k[0]][k[1]]['strength'])])
        export_edge_list(G_friend,filename="TKYedges"+"_"+str(j)+"_"+str(i)+".csv")
