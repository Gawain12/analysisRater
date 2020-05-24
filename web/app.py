import re

import jieba
from flask import Flask, render_template, url_for, request,session,redirect,g
import json
import pymysql
from zhon.hanzi import punctuation

from Douban.Spider import Movie3
from Douban.Analysis import DataProcessing
from Douban.Database.myDb import *
#import Spider.Movie3
app = Flask(__name__)
app.secret_key = '!@#$%^&*()11'
app.debug = True


engine, db_session = connection_to_mysql()
connection = pymysql.connect(host='localhost',user='root',passwd='password',db='douban',port=3306,charset='utf8')
cur=connection.cursor()
cur1=connection.cursor()

'''@app.route('/ss', methods=['GET', 'POST'])
def hello_world():
    return render_template('chart.html')'''

'''@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('index.html')
	if request.method == 'POST':
		if request.form.get('username') == 'anwen':
			session['user'] = request.form.get('username')
			return redirect('/')'''

@app.route('/test/<name>', methods=['GET'])
def test(name):
    print(name)
    return render_template('/chart.html',name=name)

@app.route('/', methods=['GET', 'POST'])
def req():
    Num =  db_session.execute('select Count(*)  FROM `user`').fetchall()
    userNum=Num[0][0]
    print(userNum)
    if request.method == 'POST':
        session["user"] = request.form.get('name')
        session["password"] = request.form.get('password')
        name = session.get('user')
        print(name)
        print(session.get("password"))
        Movie3.main(name)
        print(userNum)
        return render_template('index.html',userNum=userNum,name=name)
    else:
        return render_template('index.html',userNum=userNum)

@app.route('/a')
def index():
    return render_template('index.html')

@app.route('/chart/<string:name>/',methods=['POST','GET'])
#链接数据库
def chart(name):
    print(name)
    cur.execute("select * from user where Name = '" + name + "'")
    cur1.execute("select MyComment from {}".format(name))
    data = cur1.fetchall()
    print(str(data))
    jobNameli = []
    for d in data:
        jobNameli.extend(jieba.lcut(re.sub("[{}]+".format(punctuation), "", d[0])))
    dic = {}
    for key in jobNameli:
        dic[key] = dic.get(key, 0) + 1
    print(dic)
    wordata = []
    for i in dic:
        wordata.append({"name": i, "value": dic[i], })
    print(wordata)
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
    jsonData['ynum2'] = score[0][2:6]
    jsonData['ynum'] = ynum
    jsonData['num'] = num
    jsonData['type'] = type
    jsonData['cloud'] = wordata
    j = json.dumps(jsonData)

    #依次把三个游标关闭
    #cur.close()
    #connection.close()
    return (j)

if __name__ == '__main__':

    app.run(debug=True)
