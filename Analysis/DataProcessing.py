# encoding:utf-8
# FileName: Analyze
# Author:   Gawain
# email:    tankaiyuan33@gmail.com
# Date:     2020/5/14 18:43
# Description: 个人观影分析
from flask import Flask
app = Flask(__name__)
import matplotlib
#matplotlib.use('Agg')  # 不出现画图的框
from io import BytesIO
import base64


import numpy as np
import pandas as pd

from Douban.Database.myDb import connection_to_mysql
import matplotlib.pyplot as plt
import seaborn as sns

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置可以一行显示
# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

def sns_set():
    """
    sns 相关设置
    @return:
    """
    # 声明使用 Seaborn 样式
    sns.set()
    # 有五种seaborn的绘图风格，它们分别是：darkgrid, whitegrid, dark, white, ticks。默认的主题是darkgrid。
    sns.set_style("darkgrid")
    # 有四个预置的环境，按大小从小到大排列分别为：paper, notebook, talk, poster。其中，notebook是默认的。
    sns.set_context('notebook')
    # 中文字体设置-黑体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 解决保存图像是负号'-'显示为方块的问题
    plt.rcParams['axes.unicode_minus'] = False
    # 解决Seaborn中文显示问题并调整字体大小
    sns.set(font='SimHei')

    return sns


def read_data(name):
    """
    读取数据库中的数据
    @return:
    """
    # 建立数据库连接
    engine, db_session = connection_to_mysql()
    # 写一条sql
    sql = 'select * from {}'.format(name)
    # 获取数据库中的所有数据
    data = pd.read_sql(sql, con=engine)
    """
    针对每个数据字段进行清洗
    @param df_data:
    @return:
    """

    ''' 1. 查看整体数据类型与缺失情况'''
    print(data.info())
    ''' 
     0   Id         910 non-null    int64 
 1   Name       910 non-null    object
 2   Rate       910 non-null    object
 3   MyRate     910 non-null    object
 4   Num        910 non-null    object
 5   Director   910 non-null    object
 6   Type       910 non-null    object
 7   MyComment  910 non-null    object
    影片又名信息有两个为空，其他数据均不为空
    '''
    # 对于部分影片缺失又名信息，用影片名称去填充即可
    data['MyComment'].fillna(data['MyRate'], inplace=True)
    print(data.info())

    ''' 2. 查看单个指标的数据，并进行相应的清洗操作'''

    # 3. 影片制作国家，可以看到数据形式是 xx / xx 的形式， 用 / 分割，数据规整，但需要对空格进行处理
    print(data['Type'].head(10))
    # 这里直接去空格进行替换
    data['Type'] = data['Type'].str.replace(' ', '')
    # 7. 影片总评分，影片评论数，设置为相应的数据格式即可
    print(data[['Rate', 'Num']].head(10))
    # 这里将影片总评分转换为 float、影评人数转换为 int（默认都是 object类型）
    data['Rate'] = data['Rate'].astype(float)
    data['Num'] = data['Num'].astype(int)
    type(data)
    return data


def type(df_data):
    df_data['TypeArr'] = df_data['Type'].map(lambda e: e.split('/'))
    # 将数据转换成一维数组
    movie_type_list = np.concatenate(df_data['TypeArr'].values.tolist())
    # 将一维数组重新生成 Dataframe 并统计每个类型的个数
    movie_type_counter = pd.DataFrame(movie_type_list, columns=['Type'])['Type'].value_counts()
    # 生成柱状图的数据 x 和 y
    movie_type_x = movie_type_counter.index.tolist()
    movie_type_y = movie_type_counter.values.tolist()
    print(movie_type_x)
    print(movie_type_y)
    # 画出影片类型的柱状图
    ax1 = sns.barplot(x=movie_type_x, y=movie_type_y, palette="Blues_r", )
    # Seaborn 需要通过 ax.set_title() 来添加 title
    ax1.set_title('个人观影类型统计    by:『Gawain』')
    # 设置 x/y 轴标签的字体大小和字体颜色
    ax1.set_xlabel('影片类型', fontsize=9)
    ax1.set_ylabel('类型出现次数', fontsize=5)
    # 设置坐标轴刻度的字体大小
    ax1.tick_params(axis='x', labelsize=6)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(movie_type_x)), movie_type_y):
        ax1.text(x - 0.3, y + 0.3, '%d' % y, color='black')
    #plt.show()
    return movie_type_x,movie_type_y


def view_data(df_data):
    """
    可视化分析
    @param data:
    @return:
    """
    # 声明使用 Seaborn 样式
    sns = sns_set()

    '''1. 数据认识与探索'''
    print(df_data.info())

    '''1.1. 数据异常值等分析'''
    # 由于本次数据为规整数据，无异常值数据，可以不用处理

    '''1.2. 对数值型特征进行简单的描述性统计，包括均值，中位数，众数，方差，标准差，最大值，最小值等'''
    print(df_data.describe())
    # 通过描述性统计结果客粗略的判断存在着异常值的特征

    '''1.3. 判断这些特征都是什么数据类型？定类？定序？定距？还是定比？'''
    # 提示：弄清楚这一步主要是为了后续正确找对方法进行可视化
    '''
    影片类型、影片制片国家、影片语言: 定类数据
    影片片长、影片总评分、影片评论数、影片时间：定距数据
    影片5/4/3/2/1星占比：定比数据
    '''

    '''2. 数据可视化探索'''
    '''
    提示：根据上面自己对各个特征数据类型的判断，选择合适的可视化方法完成可视化。
    '''

    '''2.1 定类/定序特征分析'''
    '''2.1.1 将影片类型数据通过 / 分割后统计每个类型出现的次数'''
    df_data['TypeArr'] = df_data['Type'].map(lambda e: e.split('/'))
    # 将数据转换成一维数组
    movie_type_list = np.concatenate(df_data['TypeArr'].values.tolist())
    # 将一维数组重新生成 Dataframe 并统计每个类型的个数
    movie_type_counter = pd.DataFrame(movie_type_list, columns=['Type'])['Type'].value_counts()
    # 生成柱状图的数据 x 和 y
    movie_type_x = movie_type_counter.index.tolist()
    movie_type_y = movie_type_counter.values.tolist()

    # 画出影片类型的柱状图
    ax1 = sns.barplot(x=movie_type_x, y=movie_type_y, palette="Blues_r", )
    # Seaborn 需要通过 ax.set_title() 来添加 title
    ax1.set_title('个人观影类型统计    by:『Gawain』')
    # 设置 x/y 轴标签的字体大小和字体颜色
    ax1.set_xlabel('影片类型', fontsize=9)
    ax1.set_ylabel('类型出现次数', fontsize=5)
    # 设置坐标轴刻度的字体大小
    ax1.tick_params(axis='x', labelsize=6)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(movie_type_x)), movie_type_y):
        ax1.text(x - 0.3, y + 0.3, '%d' % y, color='black')
    plt.show()
    '''2.1.2导演出现次数'''
    df_data['DirectorArr'] = df_data['Director'].map(lambda e: e.split('/'))
    movie_dir_list = np.concatenate(df_data['DirectorArr'].values.tolist())
    # 将一维数组重新生成 Dataframe 并统计每个类型的个数
    movie_dir_counter = pd.DataFrame(movie_dir_list, columns=['Director'])['Director'].value_counts().head(10)
    # 生成柱状图的数据 x 和 y
    movie_dir_x = movie_dir_counter.index.tolist()
    movie_dir_y = movie_dir_counter.values.tolist()

    # 画出影片类型的柱状图
    ax1 = sns.barplot(x=movie_dir_x, y=movie_dir_y, palette="Blues_r", )
    # Seaborn 需要通过 ax.set_title() 来添加 title
    ax1.set_title('个人观影类型统计    by:『Gawain』')
    # 设置 x/y 轴标签的字体大小和字体颜色
    ax1.set_xlabel('影片导演', fontsize=3)
    ax1.set_ylabel('导演出现次数', fontsize=8)
    # 设置坐标轴刻度的字体大小
    ax1.tick_params(axis='x', labelsize=6)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(movie_dir_x)), movie_dir_y):
        ax1.text(x - 0.3, y + 0.3, '%d' % y, color='blue')
    plt.show()
    ''''2.1.2 同理将影片语言数据通过 / 分割后统计每个语言出现的次数'''

    '''2.2 定距/定比特征分析'''

    '''2.2.2 将影片总评分数据通过箱型图展示'''
    ax5 = sns.swarmplot(x=np.ones(df_data.shape[0]), y='Rate', data=df_data)
    ax5.set_title('豆瓣总评分统计    by:『Gawain』')
    ax5.set_xlabel('影片总评分分布', fontsize=10)
    ax5.set_ylabel('影片总评分', fontsize=10)
    plt.show()

    ''''2.2.3 将影片评论数数据通过箱型图展示'''
    ax6 = sns.swarmplot(x=np.ones(df_data.shape[0]), y='Num', data=df_data)
    ax6.set_title('影片评论数统计    by:『Gawain』')
    ax6.set_xlabel('影片评论数分布', fontsize=10)
    ax6.set_ylabel('影片评论数（个）', fontsize=10)
    plt.show()

    '''3. 组合特征分析'''

    print(df_data.sort_values(by='Director', ascending=False)[
              ['Name', 'Rate', 'Director', 'Num','MyRate', 'Type','MyComment']].head(10))
    print(df_data.sort_values(by='MyRate', ascending=False)[
              ['Name', 'Rate', 'Director','Num', 'MyRate', 'Type']].head(15))
    print(df_data.sort_values(by='Rate')[
              ['Name', 'Rate', 'Director','Num', 'MyRate', 'Type']].head(15))
    print(df_data.sort_values(by=['Num', 'Rate'], ascending=False)[
              ['Name', 'Rate', 'Director','Num','MyRate', 'Type']].head(15))
    # '''思考：影片排序依据'''
    # # 影片评论数进行特征缩放：采用归一化进行特征缩放
    # min_user_x = np.min(df_data['movie_comments_user'], 0)  # 按列获取最小值
    # max__user_x = np.max(df_data['movie_comments_user'], 0)  # 按列获取最大值
    # # 归一化特征缩放
    # df_data['movie_comments_user'] = (df_data['movie_comments_user'] - min_user_x) / (max__user_x - min_user_x)
    #
    # # 影片评分进行特征缩放：采用归一化进行特征缩放
    # min_rating_x = np.min(df_data['movie_rating'], 0)  # 按列获取最小值
    # max__rating_x = np.max(df_data['movie_rating'], 0)  # 按列获取最大值
    # # 归一化特征缩放
    # df_data['movie_rating'] = (df_data['movie_rating'] - min_rating_x) / (max__rating_x - min_rating_x)
    # print(df_data['movie_rating'])

    # 通过sklearn 进行数据归一化
    from sklearn import preprocessing

    df_data['Rate'] = preprocessing.normalize(df_data[['Rate']], axis=0)
    df_data['Num'] = preprocessing.normalize(df_data[['Num']], axis=0)
    # 线性相关吗？画图吧
    sns.lmplot('Num', 'Rate', df_data, order=4)
    ax = plt.gca()
    ax.set_title('总评分与评论数线性相关？    by:『Gawain』')
    ax.set_xlabel('影片评论数', fontsize=10)
    ax.set_ylabel('影片总评分', fontsize=10)
    plt.show()

    """# 转成图片的步骤
    sio = BytesIO()
    plt.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    print(data)
    html ='''
       <html>
           <body>
               <img src="data:image/png;base64,{}" />
           </body>
        <html>
    '''
    plt.close()
    # 记得关闭，不然画出来的图是重复的
    return html.format(data)"""

if __name__ == '__main__':
    data =read_data("mylist")
    #data = reshape_data(data)
    #print("*"*50)
    #type(data)
    #app.run(debug=True)
