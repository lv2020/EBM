import networkx as nx
import numpy as np
import pandas as pd
import os,time,threading
import matplotlib.pyplot as plt
os.chdir('/Users/lvvv/Project')
from multiprocessing import Process

class draw():
    def __init__(self,nodes,lc,gc,tri,i,j):
        plt.rcParams['figure.figsize']=(25,9)

        plt.subplot(1,3,1)
        plt.scatter(nodes,lc)
        plt.title('lc_'+str(i)+'_'+str(j))

        plt.subplot(1,3,2)
        plt.scatter(nodes,gc)
        plt.title('gc_'+str(i)+'_'+str(j))

        plt.subplot(1,3,3)
        plt.scatter(nodes,tri)
        plt.title('tri_'+str(i)+'_'+str(j))
        
        plt.savefig('TKY_'+str(i)+'_'+str(j)+'.png')
        plt.clf()
		
#根据之前计算好的数据重新构建graph
def build_graph(i,j):
    t1=time.clock()
    #读取数据，i表示关系强度的阈值，j表示签到时间的跨度
    train_data=pd.read_csv('TKYedges_'+str(i)+'_'+str(j)+'.csv')
    G=nx.Graph()
    for i in range(len(train_data['Source'])):
        G.add_weighted_edges_from([(train_data['Source'][i],train_data['Target'][i],train_data['Weight'][i])])
    print("bulid graph用时为：", time.clock()-t1)
    return G

#计算局部中心度
def local_centrality(G):
    t1=time.clock()
    num=len(G.nodes())
    local_centrality=[]
    for i in G.nodes():
        local_centrality.append(G.degree(i)/num)
    print("local centrality用时为：", time.clock()-t1)
    return local_centrality

#计算全局中心度
def global_centrality(G):
    t1=time.clock()
    nodes=list(G.nodes())
    global_centrality=[]
    for i,j in enumerate(nodes):
        global_centrality.append(0)
        for m in nodes[i:]:
            try:
            	#获得带权路径长度
                global_centrality[i]+=nx.dijkstra_path_length(G,j,m)
            except:
            	#有些没有相连的点先不考虑
                continue
    print("global centrality用时为：", time.clock()-t1)
    return global_centrality

#def betweenness_proportion(G):
#计算三角关系数量
def triangle(G):
    t1=time.clock()
    nodes=list(G.nodes())
    tri=[]
    for h,i in enumerate(nodes):
        G.nodes[i]['triangle']=[]
        neighbors=list(G.neighbors(i))
        tri.append(0)
        if(len(neighbors)<3):
            continue
        else:
            for m,n in enumerate(neighbors):
                for k in neighbors[m:]:
                	#判断是否为三角
                    if((n,k) in G.edges() and n!=i and k!=i):
                        G.nodes[i]['triangle'].append((i,n,k))
                        tri[h]+=1
    print("triangle用时为：", time.clock()-t1)
    return tri

#把前面所有的进行统一，为进行并发进行修改
def analysis_max(j):
	t1=time.clock()
	for i in [0.6825,0.683,0.6835]:
		G=build_graph(i,j)
		lc=local_centrality(G)
		gc=global_centrality(G)
		tri=triangle(G)
		nodes=list(G.nodes())

		#画图，便于分析
		a=draw(nodes,lc,gc,tri,i,j)
	print("------------------------------------------")
	print("total time:",time.clock()-t1)
	print("------------------------------------------\n")

#分析随参数变化的消失的点和边的比例，返回不同参数的点和边的数量
def analysis_nodes_edges():
	nodes=[[] for i in range(6)]
	edges=[[] for i in range(6)]
	G=build_graph(0.68,3600)
	nodes_max=len(G.nodes())
	edges_max=len(G.edges())
	for j in range(600,4200,600):
		for i in [0.68,0.682,0.684,0.685,0.686,0.688,0.69]:
			G=build_graph(i,j)
			
			plt.subplot(1,2,1)
			plt.xlim(0.675,0.695)
			nodes[int(j/600)-1].append(len(G.nodes()))
			plt.scatter(i,j,c='b',alpha=len(G.nodes())/nodes_max)
			
			plt.subplot(1,2,2)
			plt.xlim(0.675,0.695)
			edges[int(j/600)-1].append(len(G.edges()))
			plt.scatter(i,j,c='b',alpha=len(G.edges())/edges_max)
	plt.savefig('nodes_edges_trend.png')
	return nodes,edges

#六进程并发
def mul_process_max():
	print("Parent process %s."%(os.getpid()))
	for i in range(6):
		#创建进程
		p = Process(target=analysis_max,args=(600*(i+1),))
		print("Process will start.")
		p.start()
	p.join()
	print("Process end")
