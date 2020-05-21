import re

import jieba
from flask import Flask, render_template, url_for, request
import json
import pymysql
from zhon.hanzi import punctuation

from Analysis import DataProcessing
from Database.myDb import *
#import Spider.Movie3
app = Flask(__name__)
from Spider import Movie3

engine, db_session = connection_to_mysql()
connection = pymysql.connect(host='localhost',user='root',passwd='password',db='douban',port=3306,charset='utf8')
cur=connection.cursor()
cur1=connection.cursor()

@app.route('/ss')
def hello_world():
    return render_template('chart.html')

@app.route('/s', methods=['GET', 'POST'])
def req():
    Num =  db_session.execute('select Count(*)  FROM `user`').fetchall()
    userNum=Num[0][0]
    print(userNum)
    if request.method == 'POST':
        name = request.form.get('name')
        print(name)
        Movie3.main(name)
        print(userNum)
        return render_template('index.html',userNum=userNum,name=name)
    else:
        return render_template('index.html',userNum=userNum)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart',methods=['POST'])
#链接数据库
def chart(name='gawaint'):
    cur.execute("select * from user where Name = '" + name + "'")
    cur1.execute("select MyComment from gawain ")
    data = cur1.fetchall()
    print(str(data))
    jobNameli = []
    for d in data:
        jobNameli.extend(jieba.lcut(re.sub("[{}]+".format(punctuation), "", d[0])))
    dic = {}
    for key in jobNameli:
        dic[key] = dic.get(key, 0) + 1
    print(dic)
    worldata = []
    for i in dic:
        worldata.append({"name": i, "value": dic[i], })
    print(worldata)
    score = cur.fetchall()
    print(score[0])
    data = DataProcessing.read_data(name)
    type, num = DataProcessing.type(data)

    xname = []
    ynum = []
    jsonData = {}
    #将数据转化格式方便在HTML中调用

    jsonData['xname'] = xname
    jsonData['ynum'] = ynum
    jsonData['ynum2'] = score[0][2:7]
    jsonData['ynum'] = ynum
    jsonData['num'] = num
    jsonData['type'] = type
    jsonData['cloud'] = worldata
    j = json.dumps(jsonData)

    #依次把三个游标关闭
    cur.close()
    connection.close()
    return (j)

if __name__ == '__main__':

    app.run(debug=True)
