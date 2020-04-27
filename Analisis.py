import pymysql
import pandas as pd

# 与 mysql 建立连接
conn = pymysql.connect('localhost','username','password','douban')
# sql 语句定义为一个字符串
sql_search = 'select question_id from topic_monitor where is_title=0 ;'
# 调用 pandas 的 read_sql() 方法拿到 dataframe 结构的数据
question_ids = pd.read_sql(sql_search,conn)
# 关闭连接
conn.close()