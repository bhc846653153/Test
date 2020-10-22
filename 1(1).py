#数据分析
import pandas as pd
from math import radians, cos, sin, asin, sqrt

#数据查看
df = pd.read_csv("mobike_shanghai_sample_updated.csv",sep=",",parse_dates=["start_time","end_time"])  # 导入csv数据文件,将start_time转换为日期列，避免后续字符串和datetime的转换
df.head()  #查看前5条数据集
df.info()  #查看字段 其中orderid 订单号,bikeid 车辆ID,userid 用户ID,starttime 骑行起始日期时间,start_location_和start_location_y骑行起始位置.endtime 骑行终止日期时间end_location_和end_location_y骑行终止位置.track轨迹
df.shape   #数据集大小
df.bikeid.unique().size   #数据涵盖了近8万的单车，unique函数去除其中重复的元素，并按元素由大到小返回一个新的无重复元素
df.userid.unique().size   # 数据涵盖了1万+的骑行用户
df.describe()  #描述性统计



####单车骑行轨迹（track）####

def geodistance(item):  #用haversine公式计算球面两点间的距离
        lng1_r, lat1_r, lng2_r, lat2_r, = map(radians,[item["start_location_x"],item["start_location_y"],item["end_location_x"],item["end_location_y"]]) #将经纬度转换为弧度
        dlon = lng1_r - lng2_r
        dlat = lat1_r - lat2_r
        dis = sin(dlat/2)**2 + cos(lat1_r ) * cos(lat2_r) * sin(dlon/2)**2
        distance = 2 * asin(sqrt(dis)) * 6317 * 1000 #地球的平均半径为6371km
        distance = round(distance/1000,3)
        return distance
df["distance"] = df.apply(geodistance,axis=1)


def geoaadderLength(item):   #通过单车的轨迹获取每次交易骑行的路径
    track_list = item["track"].split("#")
    adderLength_item ={}
    adderLength = 0
    for i in range (len(track_list)-1):
        start_loc = track_list[i].split(",")
        end_loc = track_list[i+1].split(",")
        adderLength_item["start_location_x"],adderLength_item["start_location_y"] = float(start_loc[0]),float(start_loc[1])
        adderLength_item["end_location_x"],adderLength_item["end_location_y"] = float(end_loc[0]),float(end_loc[1])
        adderLength_each = geodistance(adderLength_item)
        adderLength = adderLength_each + adderLength
    return adderLength
df["adderLength"] = df.apply(geoaadderLength,axis=1)


#时间处理
df["weekday"] = df["start_time"].apply(lambda s: s.weekday())   #使用weekday函数提取周几信息，周一为0，周日为6
df["hour"] = df["start_time"].apply(lambda s: s.hour)   #提取小时数，hour属性
df["day"] = df["start_time"].apply(lambda s:str(s)[:10]) # 提取时间中的日期


#自行车被用的频率=使用次数/使用时间） #使用时间=（结束的时间-开始的时间）累加求和
df["bikeid"].value_counts()  #value_counts确认数据出现的频率
df["lag"] = (df.end_time-df.start_time).dt.seconds/60  #自行车被使用的总时间'
t = df.groupby([df["bikeid"],df["lag"]]).sum()

df3['index1'] = df3.index
t1 = df['bikeid'].groupby(df['bikeid']).count()
df["lag"] = (df.end_time-df.start_time).dt.seconds/60  #自行车单词被使用的总时间
t2 = df['lag'].groupby(df["bikeid"]).sum()  #相同id的单车每次使用的总时长
t2.reset_index().sort_values('lag',ascending = False).set_index('bikeid')  #对总时长进行排序
# t1.index.name = None

df3 = pd.merge(t1, t2,left_index=True, right_on='bikeid', how="left")  #把索引列当作连接键,left_index=True, right_index=True或者left_index=True, right_on=‘学号’，表示左表连接键作为索引、右边连接键作为普通列
# df3.index.name = None
df3['index1'] = df3.index  #生成bikeid列
df3.columns=['num','lay','bikeid']  #用columns改表头num、lay、bikeid
df3['bktime']= df3['lay']/df3['num']  #计算自行车被使用的频率：自行车被用的频率=使用次数/使用时间）

df3 = df3[['bikeid','bktime']]

#单车的描述性统计
# times = df.groupby('bikeid', as_index=False).sum()

#起始位置&结束位置(track[0][-1])
#空闲单车&紧缺单车(瓜分区块，原的数量，后的数量)
