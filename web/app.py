import os
import re
import time

import jieba
from flask import Flask, render_template, url_for, request, session, redirect, g, make_response, send_from_directory, \
    Response
import json
import pymysql
from zhon.hanzi import punctuation


from Spider.Movie3 import *
from Analysis import DataProcessing
from Database.myDb import *
app = Flask(__name__)
app.secret_key = '!@#$%^&*()11'
app.debug = True
import redis

pool = redis.ConnectionPool(host='localhost', port=6379)
conn = redis.Redis(connection_pool=pool)

engine, db_session = connection_to_mysql()

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
        main(name)
        na=conn.lrange('{}'.format(name),0,1)
        num=int(na[1])
        nick=na[0]
        print(userNum)
        return render_template('index.html',userNum=userNum,name=name,num=num,nick=nick)
    else:
        return render_template('index.html',userNum=userNum)

@app.route('/a')
def index():
    return render_template('index.html')

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response

@app.route('/progress/<string:name>/')
def progress(name):
    def generate():
        x=1
        while x < 15:
            #Num = db_session.execute("select Count(*) from {}".format('name')).fetchall()
            #x = int(conn.get('task'))
            print('Progress of %s'%name)
            x = int(conn.get('%s progress'%name))
            time.sleep(0.1)
            print('web %s' % x)
            yield "data:" + str(x) + "\n\n"
    return Response(generate(), mimetype='text/event-stream')


@app.route('/chart/<string:name>/',methods=['POST','GET'])
#链接数据库
def chart(name):
    print('Its %s Chart' %name)
    data = db_session.execute("select MyComment from {}".format(name)).fetchall()
    print(str(data))
    wordCloud = []
    for d in data:
        wordCloud.extend(jieba.lcut(re.sub("[{}]+".format(punctuation), "", d[0])))
    dic = {}
    for key in wordCloud:
        dic[key] = dic.get(key, 0) + 1
    print(dic)
    wordata = []
    for i in dic:
        wordata.append({"name": i, "value": dic[i], })
    print(wordata)
    score = db_session.execute("select * from user where Name = '" + name + "'").fetchall()
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

    return (j)

if __name__ == '__main__':

    app.run(debug=True)
