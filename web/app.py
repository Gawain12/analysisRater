import os
import re
import time

import jieba
from flask import Flask, render_template, url_for, request, session, redirect, g, make_response, send_from_directory, \
    Response
import json
from zhon.hanzi import punctuation


import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import REDIS_CONFIG
from scrapers.douban_scraper import *
from Analysis import DataProcessing
from Database.myDb import *
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = '!@#$%^&*()11'
app.debug = True
import redis

pool = redis.ConnectionPool(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'], db=REDIS_CONFIG['db'], decode_responses=True)
conn = redis.Redis(connection_pool=pool)

engine, db_session = connection_to_mysql('gawaint')

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
    Num =  db_session.execute(text('select Count(*)  FROM `user`')).fetchall()
    userNum=Num[0][0]
    print(userNum)
    if request.method == 'POST':
        session["user"] = request.form.get('name')
        session["password"] = request.form.get('password')
        name = session.get('user')
        print(name)
        main(name)
        na = conn.lrange('user:{}'.format(name), 0, 1)
        num = int(na[1])
        nick = na[0]
        print(session.get("password"))

        print(userNum)
        return render_template('index.html',userNum=userNum,name=name,num=num,nick=nick)
    else:
        return render_template('index.html',userNum=userNum, name=None)




@app.route('/a')
def index():
    Num = db_session.execute(text('select Count(*)  FROM `user`')).fetchall()
    userNum = Num[0][0]
    return render_template('index.html',userNum=userNum)

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = f"attachment; filename={filename.encode().decode('latin-1')}"
    return response

@app.route('/progress/<string:name>/')
def progress(name):
    def generate():
        x=1
        while x <= 100 and name:
            #Num = db_session.execute("select Count(*) from {}".format('name')).fetchall()
            print('Progress of %s'%name)
            progress = conn.get('progress:{}'.format(name))
            x = int(progress) if progress is not None else 0
            time.sleep(1)
            print('web %s' % x)
            yield "data:" + str(x) + "\n\n"
    return Response(generate(), mimetype='text/event-stream')


@app.route('/chart/<string:name>/',methods=['POST','GET'])
#链接数据库
def chart(name):
    print('Its %s Chart' %name)
    data = db_session.execute(text("select MyComment from `{}` where MyComment<>'还未评价'".format(name))).fetchall()
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
    score = db_session.execute(text("select * from user where Name = :name"), {'name': name}).fetchall()
    print(score[0])
    data = DataProcessing.read_data(name)
    type_list, num = DataProcessing.type(data)

    xname = [item[0] for item in type_list]
    ynum = [item[1] for item in type_list]
    jsonData = {}
    #将数据转化格式方便在HTML中调用

    jsonData['xname'] = xname
    jsonData['ynum'] = ynum
    jsonData['ynum2'] = score[0][2:6]
    jsonData['num'] = num
    jsonData['type'] = type_list
    jsonData['cloud'] = wordata
    j = json.dumps(jsonData)

    return (j)

if __name__ == '__main__':

    app.run(debug=True)
