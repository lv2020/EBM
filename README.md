# EBM
LBSN based on foursquare dataset  
EBM_graph.py是主体部分，覆盖了所有的过程。  
EBM_funcation.py则定义了所有的辅助函数，包括以下函数：  
venue_choice 对数据进行筛选，去除没有co-occurence 的地点  
time_div 了解时间分布，仅用于了解数据情况  
co_occurrence 计算co_occurrence vector 和统计不同venue的co-occurence时间数据  
location_entropy 计算location_entropy  
diversity 计算diversity  
frequency 计算frequency  
socail_strength 计算socail_strength  
drawGraph  画图函数，用于显示整个社交网络的状况  
export_edge_list  输出边表，用于下一步的分析和gephi可视化  
venue_time_draw  可视化，划分不同venue的时间分布，需要先调用co_occurrence获得VCI  
main 主体函数，用于把前面所有的函数连接起来，计算socail strength并且对一部分数据进行可视化  
cal 把main函数结果使用export_edge_list进行保存，便于下一步处理  


