# EBM
LBSN based on foursquare dataset  
EBM_graph.py是主体部分，覆盖了所有的过程。  
EBM_funcation.py则定义了所有的辅助函数，包括以下函数：  
1. venue_choice  
对数据进行筛选，去除没有co-occurence 的地点   
2. time_div  
了解时间分布，仅用于了解数据情况  
3. co_occurrence  
计算co_occurrence vector 和统计不同venue的co-occurence时间数据  
4. location_entropy  
计算location_entropy  
5. diversity  
计算diversity  
6. frequency  
计算frequency  
7. socail_strength  
计算socail_strength  
8. drawGraph  
画图函数，用于显示整个社交网络的状况  
9. export_edge_list  
输出边表，用于下一步的分析和gephi可视化  
10. venue_time_draw  
可视化，划分不同venue的时间分布，需要先调用co_occurrence获得VCI  
11. main  
主体函数，用于把前面所有的函数连接起来，计算socail strength并且对一部分数据进行可视化  
12. cal  
把main函数结果使用export_edge_list进行保存，便于下一步处理  
  
EBM_analysis.py则对之前的数据进行处理，分析不同参数对网络属性的影响。包括以下函数：  
1. build_graph  
根据之前计算好的边表重新构建图  
2. local_centrality  
计算局部中心度  
3. global_centrality  
计算全局中心度  
4. triangle  
计算三角关系数量  
5. analysis_max  
把前面的函数连接起来，统一处理  
6. analysis_nodes_edges  
分析随参数变化的消失的点和边的比例  
7. mul_process_max  
多进程并发，加快运算速度。单个核心最长运行时间大概两个半小时
  
  
edges_csv文件夹含有不同参数的边表，第一个参数是socail strength，第二个参数是时间间隔  
pictures文件夹含有网络属性的可视化结果，包括局部中心度、全局中心度和三角关系数量随两个参数的变化情况；点和边的数量随两个参数的变化情况；不同venue的打卡时间和时间间隔的关系。  

