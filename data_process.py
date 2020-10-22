import inline as inline
import pandas as pd
import datetime
# import geohash
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline

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