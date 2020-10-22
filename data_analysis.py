# import all packages and set plots to be embedded inline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
plt.show()
#%matplotlib inline

rawdata = pd.read_csv('mobike_shanghai_sample_updated.csv')
rawdata.head()

# 复制数据集，并更改各列的数据类型
mobike = rawdata.copy()
tobestr = ['orderid', 'bikeid', 'userid']
mobike[tobestr] = mobike[tobestr].astype('str')
mobike['start_time'] = pd.to_datetime(mobike['start_time'])
mobike['end_time'] = pd.to_datetime(mobike['end_time'])
mobike.info()

#新增骑行时长duration等列（通过起始时间计算），并通过字符串拆分将骑行时长单位统一为minutes（命名为ttl_min列）
mobike['duration'] = mobike.end_time - mobike.start_time
mobike['dur_day'] = mobike.duration.apply(lambda x: str(x).split(' ')[0])
mobike['dur_hr'] = mobike.duration.apply(lambda x: str(x).split(' ')[-1][:2])
mobike['dur_min'] = mobike.duration.apply(lambda x: str(x).split(':')[-2])
mobike['dur_sec'] = mobike.duration.apply(lambda x: str(x).split(':')[-1])
tobeint = ['dur_day', 'dur_hr', 'dur_min', 'dur_sec']
mobike[tobeint] = mobike[tobeint].astype('int')
mobike['ttl_min'] = mobike.dur_day * 24 * 60 + mobike.dur_hr * 60 + mobike.dur_min + mobike.dur_sec / 60
# # 保存为csv文件
min_num_data = mobike['ttl_min']
min_num_data.to_csv("min_num_data.csv")
#对csv文件追加列
data = pd.read_csv('rawdata')
print(data.columns)#获取列索引值
data1  = data['flow']#获取列名为flow的数据作为新列的数据
data['cha'] = data1 #将新列的名字设置为cha
data.to_csv(r"平均值12.csv",index =False)
#mode=a，以追加模式写入,header表示列名，默认为true,index表示行名，默认为true，再次写入不需要行名
print(data)


#新增dayid和daytype列，获取每条记录是星期几，并根据工作日和周末进行分类
mobike['dayid'] = mobike.start_time.apply(lambda x: x.isoweekday())
mobike['daytype'] = mobike.dayid.apply(lambda x: 'weekends' if x == 6 or x == 7 else 'weekdays')
# # 保存为csv文件
daytype_data = mobike['daytype']
daytype_data.to_csv("daytype_data.csv")

#新增hourid和hourtype列，获取每条记录是几点开始的，并根据早晚高峰和平峰时段进行分类
mobike['hourid'] = mobike.start_time.apply(lambda x: x.utctimetuple().tm_hour)
mobike['hourtype'] = mobike.hourid.apply(lambda x: 'rush hours' if (x >= 7 and x <= 8) or (x >= 17 and x <= 20) else 'non-rush hours')
# # 保存为csv文件
hourtype_data = mobike['hourtype']
hourtype_data.to_csv("hourtype_data.csv")


#新增distance和distocenter列，获取每条记录骑行起始点的直线距离和距离上海中心点的距离（km）
# 按每条记录的起点位置，作为发起订单所处位置的数据依据
from math import radians, cos, sin, asin, sqrt

# 自定义函数，通过两点的经纬度计算两点之间的直线距离
def geodistance(lng1, lat1, lng2, lat2):
    lng1_r, lat1_r, lng2_r, lat2_r = map(radians, [lng1, lat1, lng2, lat2]) # 经纬度转换成弧度
    dlon = lng1_r - lng2_r
    dlat = lat1_r - lat2_r
    dis = sin(dlat/2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon/2)**2
    distance = 2 * asin(sqrt(dis)) * 6371 * 1000 # 地球平均半径为6371km
    distance = round(distance/1000,3)
    return distance

# 自定义函数，通过调用geodistance获取每条记录骑行始末点和起点距中心点的直线距离
def get_dis(item):
    item['distance'] = geodistance(item['start_location_x'], item['start_location_y'],
                                   item['end_location_x'], item['end_location_y'])    # 计算骑行始末点经纬度的直线距离
    # 国际饭店一般被认为是上海地理中心坐标点，计算骑行起始点经纬度和国际饭店经纬度的直线距离
    item['distocenter'] = geodistance(item['start_location_x'], item['start_location_y'], 121.471632, 31.233705)
    return item

mobike['distance'] = np.nan
mobike['distocenter'] = np.nan
mobike = mobike.apply(get_dis, axis=1)#axis=0代表往跨行（down)，而axis=1代表跨列（across)
# # 保存为csv文件
distance_data = mobike['distance']
distance_data.to_csv("distance_data.csv")

distocenter_data = mobike['distocenter']
distocenter_data.to_csv("distocenter_data.csv")



#新增ring_stage列，对四级环线范围进行分类
# 自定义函数，按照每条记录距离上海中心点（国际饭店）的距离，根据上海内中外环线进行粗略的地理位置分类
def get_ring(item):
    if item['distocenter'] <= 10:
        item['ring_stage'] = 'inside inner ring'    # 内环距国际饭店最远距离约为10km
    elif item['distocenter'] <= 15:
        item['ring_stage'] = 'inside middle ring'    # 中环距国际饭店最远距离约为15km
    elif item['distocenter'] <= 18:
        item['ring_stage'] = 'inside outer ring'    # 外环距国际饭店最远距离约为18km
    elif item['distocenter'] > 18:
        item['ring_stage'] = 'outside outer ring'
    return item

mobike['ring_stage'] = np.nan
mobike = mobike.apply(get_ring, axis = 1)

# # 保存为csv文件
ring_stage_data = mobike['ring_stage']
ring_stage_data.to_csv("ring_stage_data.csv")



# #用户RFM模型分级
# #新增cost列，以用于后续计算
# import math
# mobike['cost'] = mobike.ttl_min.apply(lambda x: math.ceil(x/30))    # 参照2016年摩拜收费标准，按每30分钟收取1元进行cost列的粗略计算
#
# #计算RFM值
# # 建立副本，将用户id以数字大小进行排序，以便后续rfm值计算时每条记录的顺序保持一致
# mobike_sub = mobike.copy()
# mobike_sub.userid = mobike_sub.userid.astype('int')
# mobike_sub = mobike_sub.sort_values('userid')
#
# # 计算RFM值，并制作新的dataframe
# mobike_sub['r_value_single'] = mobike_sub.start_time.apply(lambda x: 32 - x.timetuple().tm_mday)    # 因数据集仅包含八月份发起的订单数据，故以9/1为R值计算基准
# r_value = mobike_sub.groupby(['userid']).r_value_single.min()    # 按每个用户id所有订单日期距9/1相差天数的最小值作为r值
# f_value = mobike_sub.groupby(['userid']).size()    # 按每个用户id八月累积订单数量计算f值
# m_value = mobike_sub.groupby(['userid']).cost.sum()    # 按每个用户id八月累积消费金额作为m值
# rfm = pd.DataFrame({'r_value': r_value, 'f_value': f_value, 'm_value': m_value})    # 将三个series合并为新的dataframe
#
# # 查看rfm数据概要
# rfm.describe()
#
# #进行RFM评分
# # 自定义函数，分别根据rfm值，对每个用户id进行打分
# def get_rfm(item):
#     # 为r_value评级
#     if item.r_value < 4:
#         item['r_score'] = 3
#     if item.r_value <= 13 and item.r_value >= 4:
#         item['r_score'] = 2
#     if item.r_value > 13:
#         item['r_score'] = 1
#     # 为f_value评级
#     if item.f_value > 10:
#         item['f_score'] = 3
#     if item.f_value <= 10 and item.f_value >= 6:
#         item['f_score'] = 2
#     if item.f_value < 6:
#         item['f_score'] = 1
#     # 为m_value评级
#     if item.m_value > 9:
#         item['m_score'] = 3
#     if item.m_value <= 9 and item.m_value >= 7:
#         item['m_score'] = 2
#     if item.m_value < 7:
#         item['m_score'] = 1
#     return item
#
# rfm['r_score'] = np.nan
# rfm['f_score'] = np.nan
# rfm['m_score'] = np.nan
# rfm = rfm.apply(get_rfm, axis = 1)
#
# # 查看rfm评分数据分布情况是否合理
# print(rfm.r_score.value_counts())
# print(rfm.f_score.value_counts())
# print(rfm.m_score.value_counts())
#
# #计算每个用户RFM总分，并进行用户分层
# rfm['score'] = rfm.r_score + rfm.f_score + rfm.m_score    # 每个用户rfm分数加总
# rfm.score.value_counts()    # 查看用户得分数据分布情况是否合理
#
# # 自定义函数，分三段进行用户分层
# def get_rate(item):
#     if item.score >= 7:
#         item.rate = 'high-value user'
#     elif item.score >= 5:
#         item.rate = 'middle-value user'
#     else:
#         item.rate = 'low-value user'
#     return item
# rfm['rate'] = np.nan
# rfm = rfm.apply(get_rate, axis = 1)
# rfm.rate.value_counts()    # 查看用户分层级别分布情况是否合理
#
# #合并dataframe
# mobike.userid = mobike.userid.astype('int')    # 先将mobike中的userid列转换为int类型，实现与rfm中int型index的匹配，以便于操作merge函数
# mobike = mobike.merge(rfm, on = 'userid', how = 'inner')
#
# mobike.info()    # 查看数据类型，以用于后续整理
#
# # 将对应列转换成字符串变量
# mobike.userid = mobike.userid.astype('str')
# # 将对应列转换成整型变量
# tobeint = ['ttl_min', 'r_value', 'f_value', 'm_value', 'r_score', 'f_score', 'm_score', 'score']
# mobike[tobeint] = mobike[tobeint].astype('int')
# # 将对应列转换成类别变量
# order_dict = {'ring_stage': ['inside inner ring', 'inside middle ring', 'inside outer ring', 'outside outer ring'],
#               'rate': ['high-value user', 'middle-value user', 'low-value user'],
#               'daytype': ['weekdays', 'weekends'],
#               'hourtype': ['rush hours', 'non-rush hours']}
# for var in order_dict:
#     order = pd.api.types.CategoricalDtype(ordered = True, categories = order_dict[var])
#     mobike[var] = mobike[var].astype(order)


#单变量探索分析
#首先查看关键分析指标骑行时长 （ttl_min）的数据分布情况
df_e = mobike.copy()
# 将对应列转换成类别变量
order_dict = {'ring_stage': ['inside inner ring', 'inside middle ring', 'inside outer ring', 'outside outer ring'],
              'rate': ['high-value user', 'middle-value user', 'low-value user'],
              'daytype': ['weekdays', 'weekends'],
              'hourtype': ['rush hours', 'non-rush hours']}
for var in order_dict:
    order = pd.api.types.CategoricalDtype(ordered=True, categories=order_dict[var])
    df_e[var] = df_e[var].astype(order)

bins = np.arange(0, df_e.ttl_min.max() + 1, 1)
plt.hist(data=df_e, x='ttl_min', bins=bins);
plt.xlabel('Riding Duration (min)');


#剔除异常数据，重新绘制直方图观察骑行时长的数据分布情况
df_e['speed'] = df_e['distance'] / (df_e['ttl_min'] / 60)
df_e = df_e[-(((df_e['speed'] < 12) | (df_e['speed'] > 20)) & ((df_e['ttl_min'] > 720) | (df_e['distance'] > 50)))]
bins = np.arange(0, df_e.ttl_min.max()+1, 1)
plt.hist(data = df_e, x = 'ttl_min', bins = bins);
plt.xlabel('Riding Duration (min)');

#查看distance的数据分布情况
bins = np.arange(0, df_e.distance.max()+0.01, 0.01)
plt.hist(data = df_e, x = 'distance', bins = bins);
plt.xlabel('Riding Distance (km)');
#plt.show()

# 骑行距离同样存在长尾分布特征，对x轴使用log变化以观察分布规律
bins = 10 ** np.arange(np.log10(df_e.distance.min()), np.log10(df_e.distance.max()) + 0.08, 0.08)
plt.hist(data = df_e, x = 'distance', bins = bins);
plt.xscale('log')
xticks = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20)
plt.xticks(xticks, xticks);
plt.xlabel('Riding Distance (km)');
plt.show()


#查看daytype、hourtype、ring_stage、rate四个类别变量的分布情况
fig, ax = plt.subplots(ncols = 2, nrows = 2, figsize = [14, 7])
color = sb.color_palette()[0]
sb.countplot(data = df_e, x = 'daytype', color = color, ax = ax[0, 0]);
sb.countplot(data = df_e, x = 'hourtype', color = color, ax = ax[0, 1]);
sb.countplot(data = df_e, x = 'ring_stage', color = color, ax = ax[1, 0]);
sb.countplot(data = df_e, x = 'rate', color = color, ax = ax[1, 1]);
plt.show()

