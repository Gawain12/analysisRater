import asyncio
import re
import sys
import requests
from fake_useragent import UserAgent
import aiohttp
import pandas as pd
import xlwt
import time
import redis

from Douban.Analysis.WeightScore import *
from Douban.Database.myDb import connection_to_mysql
#from haipproxy.client.py_cli import ProxyFetcher
import Douban.Database.myDb
pool = redis.ConnectionPool(host='localhost', port=6379,decode_responses=True)
conn = redis.Redis(connection_pool=pool)


global dfe
dfe= pd.DataFrame()
args = dict(host='127.0.0.1', port=6379, password=None, db=0)
#fetcher = ProxyFetcher('douban', strategy='greedy', redis_args=args)

ua = UserAgent()
print(ua.random)
'''
def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    proxypsslUrl = 'http://127.0.0.1:5555/random'
    return requests.get(proxypsslUrl).text.strip()
'''
class DataTool(object):
    def __init__(self):
        self.headers = {
            'User-Agent': ua.random,
        }

    def newTupleData(self,originTupleData,rates,comments):
        #print(rate*2)
        newDict = {}
        p1 = re.compile(r'<li>', re.S)
        p2 = re.compile(r'</li>', re.S)
        # pass_</span>
        p3 = re.compile(r'</span>', re.S)
        # pass_<span property=.*?>
        p4 = re.compile(r'<span property=.*?>', re.S)
        # pass_\n
        p5 = re.compile(r'\n', re.S)
        # pass_space
        p6 = re.compile(r' ', re.S)
        p7 = re.compile(r'<spanclass="comment">', re.S)
        p8= re.compile(r'</ul>', re.S)
        p9 = re.compile(r'<spanclass="tags">', re.S)
        p10 = re.compile(r'&#39;',re.S)
        p11 = re.compile(r'&#34;',re.S)
        p12 = re.compile(r'<span class="date">.*?</span>',re.S)
        p13 = re.compile(r'<spanclass="pl">',re.S)

        name = re.sub(p10, "'", originTupleData[0])
        newDict['名称'] = name

        newDict['电影评分'] =float(originTupleData[3])

        newDict['评价人数'] =float(originTupleData[4])
        newDict['导演'] = originTupleData[1]

        if rates == 'date':
            rate = 0
        else:
            rate = int(re.findall(r'\d+', rates)[0]) * 2

        gut = re.sub(p3, '', originTupleData[2])
        gut = re.sub(p4, '', gut)
        newDict['类型'] = gut

        comment = re.sub(p12, '', comments)
        comment = re.sub(p4, '', comment)
        comment = re.sub(p5, '', comment)
        comment = re.sub(p6, '', comment)
        comment = re.sub(p1, '', comment)
        comment = re.sub(p2, '', comment)
        comment = re.sub(p7, '', comment)
        comment = re.sub(p8, '', comment)
        comment = re.sub(p9, '', comment)
        comment = re.sub(p10, "'", comment)
        comment = re.sub(p11, "'", comment)
        comment = re.sub(p3, '', comment)
        comment = re.sub(p13, '', comment)

        #print(comment)
        if comment=='':
            newDict['个人评价']='还未评价'
        else:
            newDict['个人评价'] = comment

        newDict['个人评分'] = rate
        return newDict

class Data(object):

    # 读取数据
    def __init__(self):
        # 创建工作簿
        #self.cur, self.conn = mySql.CtM()

        self.engine, self.pymysql_session = connection_to_mysql()
        self.writer = pd.ExcelWriter('E:\\Desktop\\test.xlsx')
       # 写入数据
    def writeData(self,row,movieDataDict,name):
        # ----------处理电影信息------------
        # 由字典转化成列表
        global dfe
        dr = pd.DataFrame(movieDataDict,index = [0])
        eachDetail = []
        for value in movieDataDict.values():
            eachDetail.append(value)

        io = "../web/{}的片单.xlsx".format(name)
        eachDetail = eachDetail[0:-1]
        #del dr['_id']
        df = dr.astype(object).where(pd.notnull(dr), None)
        df.rename(columns={'名称': 'Name', '电影评分': 'Rate', '个人评分': 'MyRate', '评价人数': 'Num', '导演': 'Director', '类型': 'Type', '个人评价': 'MyComment'}, inplace=True)
        #print(df)
        dfe=dfe.append(df,ignore_index=True,sort=False)
        #print(dfe)
        dfe.to_excel(io, sheet_name="mylist", na_rep="NoComment", index=False)
        #df.to_csv('E:\\Desktop\\my_csv.csv', mode='a', header=False,encoding="GB18030")
        df.to_sql(name, self.engine, index=False, dtype=None, if_exists='append')


class DouBan(object):
    def __init__(self):
        self.headers = {
            'User-Agent' : ua.random,
             }
        # 设置代理ip
        #self.proxy_list = {
             #"http": "http://202.121.96.33:8086",
         #}
        self.basePageUrl = 'https://movie.douban.com/people/{}/collect?start={}'
        #self.proxies=fetcher.get_proxy()
    def Num(self,na,name):
        pageUrl = self.basePageUrl.format(name, 0)
        try:
            response = requests.get(pageUrl, headers=self.headers)
            if response.status_code == 200:
                pageHtml = response.text
                pattern = re.compile(
                    r'<div id="db-usr-profile">.*?<div class="info">.*?<h1>(.*?)看过的电影(.*?)</h1>.*?</div>',
                    re.S)
                na = re.findall(pattern, pageHtml)
                print(na)
                if na:
                 nick = na[0][0]
                 num=int(na[0][1].strip('()'))

                 print('nickName is {}'.format(nick))
                 return nick,num
                else:
                    return '没有',3
            else:
                print('请求错误：url = {}, status_code = {}'.format(pageUrl, response.status_code))
                sys.exit(0)
                return None
        except Exception as e:
            print('请求异常：url = {}, error = {}'.format(pageUrl, e))
            return None
    async def startCrawl(self,sem,session,num,name):
        # 使用代理ip
       # proxy = self.proxy_list
       # proxies = {'http' : get_random_proxy()}
       # print('get random proxy', proxies)
      #print(fetcher.get_proxy())
      async with sem:
        try:
            print('This is %s doubanlist' %name)
            print("Crawing %s" % num)
            pageUrl = self.basePageUrl.format(name,num)
            async with await session.get(pageUrl, headers=self.headers) as response:
                    if response.status == 200:
                        print('请求成功：url = {}, status = {}'.format(pageUrl, response.status))
                        responseText = await response.text()
                        print("%s 爬取完毕......" % num )
                        return responseText
                    else:
                        print('请求错误：url = {}, status = {}'.format(pageUrl, response.status))
                        sys.exit(0)
                        return None
        except Exception as e:
            print('请求异常：url = {}, error = {}'.format(pageUrl, e))
    # 获取详首页电影的movieUrl rate comment,返回一个列表


    async def myList(self,pageHtml,urlsLists):
        # 书写正则表达式
         pattern = re.compile(r'<div class="pic">.*?<a title="(.*?)" href="(.*?)" .*?>.*?<div class="info">.*?<li>.*?class="(.*?)">.*?</span>.*?(.*?)</div>', re.S)
         movieInfoList = re.findall(pattern,pageHtml)

         urlsLists.extend(movieInfoList)
         print(urlsLists)
         return urlsLists
    # 获取电影信息源码
    async def myHtml(self,sem,session,movieUrl):
     #print(fetcher.get_proxy())
     async with sem:
      try:
            async with await session.get(movieUrl,headers=self.headers) as response:
                if response.status == 200:
                    #print(response.status)
                    responseText = await response.text()
                    return responseText
                else:
                    print('请求错误：url = {}, status = {}'.format(movieUrl, response.status))

                    return None
      except Exception as e:
                print('请求异常：url = {}, error = {}'.format(movieUrl, e))
    # 获取电影的详细信息
    async def movieDetails(self,movieHtml,row,rate,comment,name):

        pattern = re.compile(r'<div id="content">.*?<h1>.*?>(.*?)</span>.*? rel="v:directedBy">(.*?)</a>.*?<span class="pl".*?</span>(.*?)<br/>.*?<span class="pl">制片国家.*?<strong class="ll rating_num" property="v:average">(.*?)</strong>.*?<span property="v:votes">(.*?)</span>',re.S)
        movie_data = re.findall(pattern,str(movieHtml))
        # 测试输出
        print(movie_data)
        for movieTuple in movie_data:
            newData = DataTool().newTupleData(movieTuple, rate, comment)
            Data().writeData(row,newData,name)
            row += 1
            conn.incr('%s progress'%name)
            print(newData)
        if movie_data is None:
            return None
        # 保存到数据库中
    async def download(self,sem,num,urlsLists,name):
        async with aiohttp.ClientSession() as session:
                html = await DouBan().startCrawl(sem,session,num,name)
                await DouBan().myList(html,urlsLists)
    async def handle(self,sem,url,row,rate,comment,name):
        async with aiohttp.ClientSession() as session:
                html = await DouBan().myHtml(sem,session,url)
                await DouBan().movieDetails(html,row,rate,comment,name)


def main(name):
    conn.set('%s progress'%name, '0')
    start = time.time()
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    dbObj = DouBan()
    row = 1
    print(name)
    CreateTb(name)
    sem = asyncio.Semaphore(100)
    urlsLists = []
    tasks = []
    na=[]
    nick,num=dbObj.Num(na,name)
    conn.rpush('{}'.format(name), nick, num)
    for i in range(0, 6):
        if i % 15 == 0:
            task = asyncio.ensure_future(dbObj.download(sem, i, urlsLists, name))
            tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

    taskList = []
    for eachUrl in urlsLists:
        rate = eachUrl[2]
        comment = eachUrl[3]
        task = asyncio.ensure_future(dbObj.handle(sem, eachUrl[1], row, rate, comment,name))
        taskList.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(taskList))

    Total = ARate(name) * 0.3 + RVolume(name) * 0.18 + Type(name) * 0.22 + Tspdt(name) * 0.3
    Users = User(Id=None,Name=name, Rvolume=RVolume(name), Type=Type(name), Tspdt=Tspdt(name), Wrate=ARate(name), Score=float(Total))
    db_session.add(Users)
    db_session.commit()
    end = time.time()
    print('Cost time:', end - start)
'''Name=web.app.req().name
print(Name)
main('lemon0406')'''