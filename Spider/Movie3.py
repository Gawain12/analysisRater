import asyncio
import re

from fake_useragent import UserAgent
import aiohttp
import pandas as pd
import xlwt
import time

from Douban.Analysis.WeightScore import *
from Douban.Database.myDb import connection_to_mysql
#from haipproxy.client.py_cli import ProxyFetcher
import Douban.Database.myDb


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

    def newTupleData(self,originTupleData,rate,comments):
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

        name = re.sub(p10, "'", originTupleData[0])
        newDict['名称'] = name

        newDict['电影评分'] =float(originTupleData[3])
        newDict['个人评分'] = rate*2

        newDict['评价人数'] =float(originTupleData[4])
        newDict['导演'] = originTupleData[1]

        gut = re.sub(p3, '', originTupleData[2])
        gut = re.sub(p4, '', gut)
        newDict['类型'] = gut

        comment = re.sub(p3, '', comments)
        comment = re.sub(p4, '', comment)
        comment = re.sub(p5, '', comment)
        comment = re.sub(p6, '', comment)
        comment = re.sub(p1, '', comment)
        comment = re.sub(p2, '', comment)
        comment = re.sub(p7, '', comment)
        comment = re.sub(p8, '', comment)
        comment = re.sub(p9, '', comment)
        comment = re.sub(p10, '', comment)
        comment = re.sub(p11, '', comment)

        #print(comment)
        newDict['个人评价'] = comment

        return newDict

class Excel(object):

    # 读取数据
    def __init__(self):
        # 创建工作簿
        #self.cur, self.conn = mySql.CtM()
        self.excelWorkBook = xlwt.Workbook('utf-8')

        # 创建一个excel表
        self.excelWorkSheet = self.excelWorkBook.add_sheet('个人豆瓣观影记录', cell_overwrite_ok=True)

        # 创建第一行 标题
        self.rowTitle = ['电影名称','豆瓣评分','个人评分','评价人数','导演','类型','个人评价']
        self.engine, self.pymysql_session = connection_to_mysql()
        # 把第一行写入表格
        for i in range(0,len(self.rowTitle)):
            self.excelWorkSheet.write(0,i,self.rowTitle[i])
        self.saveExcelData()
       # 写入数据
    def writeData(self,row,movieDataDict,name):
        # ----------处理电影信息------------
        # 由字典转化成列表
        dr = pd.DataFrame(movieDataDict,index = [0])
        eachDetail = []
        for value in movieDataDict.values():
            eachDetail.append(value)
        # 把电影数据写入表格
        for i in range(0,len(self.rowTitle)):
            self.excelWorkSheet.write(row,i,eachDetail[i])
        eachDetail = eachDetail[0:-1]
        #del dr['_id']
        df = dr.astype(object).where(pd.notnull(dr), None)
        df.rename(columns={'名称': 'Name', '电影评分': 'Rate', '个人评分': 'MyRate', '评价人数': 'Num', '导演': 'Director', '类型': 'Type', '个人评价': 'MyComment'}, inplace=True)
        #print(df)
        df.to_sql(name, self.engine, index=False, dtype=None, if_exists='append')
    def saveExcelData(self):
        # 这个保存是在建立一个工作簿那个对象进行保存的
        self.excelWorkBook.save('E:\Desktop\douban.xls')

class DouBan(object):
    def __init__(self):
        self.headers = {
            'User-Agent' : ua.random,
            'Cookie':'ll="118237"; bid=miJfnEe9C8E; __yadk_uid=C8tCYDQmeHxAfZlS5hvnGCCLtrU72prh; douban-fav-remind=1; ps=y; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1547354707%2C%22https%3A%2F%2Fopen.weixin.qq.com%2Fconnect%2Fqrconnect%3Fappid%3Dwxd9c1c6bbd5d59980%26redirect_uri%3Dhttps%253A%252F%252Fwww.douban.com%252Faccounts%252Fconnect%252Fwechat%252Fcallback%26response_type%3Dcode%26scope%3Dsnsapi_login%26state%3DmiJfnEe9C8E%252523douban-web%252523https%25253A%252F%252Fmovie.douban.com%252Ftop250%25253Fstart%25253D125%252526filter%25253D%22%5D; _pk_id.100001.4cf6=4179da9d4af6318e.1543568427.5.1547358498.1547349967.; _vwo_uuid_v2=D4FCFEDCB33DF07B2DE0DC525D42F7488|9024e242bbd9c0f98192b002e4091fc3; as="https://sec.douban.com/b?r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F26430107%2F"; dbcl2="189997368:Qj2bbphj+X0"; ck=iccT; push_noty_num=0; push_doumail_num=0'
        }
        # 设置代理ip
        #self.proxy_list = {
             #"http": "http://202.121.96.33:8086",
         #}
        self.base_pageUrl = 'https://movie.douban.com/people/{}/collect?start={}'
        #self.proxies=fetcher.get_proxy()
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
            pageUrl = self.base_pageUrl.format(name,num)
            async with await session.get(pageUrl, headers=self.headers) as response:
                    if response.status == 200:
                        print('请求成功：url = {}, status = {}'.format(pageUrl, response.status))
                        responseText = await response.text()
                        print("%s 爬取完毕......" % num )
                        return responseText
                    else:
                        print('请求错误：url = {}, status = {}'.format(pageUrl, response.status))
                        return None
        except Exception as e:
            print('请求异常：url = {}, error = {}'.format(pageUrl, e))
    # 获取详首页电影的 top_no movieUrl,返回一个列表
    async def myList(self,pageHtml,urlsLists):
        # 书写正则表达式
         pattern = re.compile(r'<div class="pic">.*?<a title="(.*?)" href="(.*?)" .*?>.*?<div class="info">.*?<li>.*?class="rating(.*?)-t">.*?class="date">.*?</span>.*?(.*?)</div>', re.S)
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
            Excel().writeData(row, newData,name)
            row += 1
            print(newData)
        Excel().saveExcelData()
        if movie_data is None:
            return None
        return movie_data
        # 保存到数据库中
    async def handle(self,sem,url,row,rate,comment,name):
        async with aiohttp.ClientSession() as session:
                html = await DouBan().myHtml(sem,session,url)
                await DouBan().movieDetails(html,row,rate,comment,name)

    async def download(self,sem,num,urlsLists,name):
        async with aiohttp.ClientSession() as session:
                html = await DouBan().startCrawl(sem,session,num,name)
                await DouBan().myList(html,urlsLists)
def main(name):

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
    for i in range(0, 10):
        if i % 15 == 0:
            task = asyncio.ensure_future(dbObj.download(sem, i, urlsLists, name))
            tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

    taskList = []
    for eachUrl in urlsLists:
        rate = int(eachUrl[2])
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
main(Name)'''
