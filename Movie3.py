import re,requests,pymongo
from queue import Queue
import _thread
import pandas as pd
from multiprocessing import Pool
import xlwt,xlrd
import time
import pymysql
from myDb import connection_to_mysql
#from fake_useragent import UserAgent

start =time.time()
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }

    def newTupleData(self,originTupleData,rate,comments):
        print(rate*2)
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
        p10 = re.compile(r'&#39;')

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

        print(comment)
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
    def write_data(self,row,movieDataDict):
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
        print(df)
        df.to_sql('mylist2', self.engine, index=False, dtype=None, if_exists='append')
    def saveExcelData(self):
        # 这个保存是在建立一个工作簿那个对象进行保存的
        self.excelWorkBook.save('E:\Desktop\douban.xls')

class DouBan(object):
    def __init__(self):
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
            'Cookie':'ll="118237"; bid=miJfnEe9C8E; __yadk_uid=C8tCYDQmeHxAfZlS5hvnGCCLtrU72prh; douban-fav-remind=1; ps=y; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1547354707%2C%22https%3A%2F%2Fopen.weixin.qq.com%2Fconnect%2Fqrconnect%3Fappid%3Dwxd9c1c6bbd5d59980%26redirect_uri%3Dhttps%253A%252F%252Fwww.douban.com%252Faccounts%252Fconnect%252Fwechat%252Fcallback%26response_type%3Dcode%26scope%3Dsnsapi_login%26state%3DmiJfnEe9C8E%252523douban-web%252523https%25253A%252F%252Fmovie.douban.com%252Ftop250%25253Fstart%25253D125%252526filter%25253D%22%5D; _pk_id.100001.4cf6=4179da9d4af6318e.1543568427.5.1547358498.1547349967.; _vwo_uuid_v2=D4FCFEDCB33DF07B2DE0DC525D42F7488|9024e242bbd9c0f98192b002e4091fc3; as="https://sec.douban.com/b?r=https%3A%2F%2Fmovie.douban.com%2Fsubject%2F26430107%2F"; dbcl2="189997368:Qj2bbphj+X0"; ck=iccT; push_noty_num=0; push_doumail_num=0'
        }
        # 设置代理ip
        #self.proxy_list = {
             #"http": "http://202.121.96.33:8086",
         #}
        self.base_page_url = 'https://movie.douban.com/people/GawainT/collect?start={}'

    def startCrawl(self,num):
        # 使用代理ip
       # proxy = self.proxy_list
       # proxies = {'http' : get_random_proxy()}
       # print('get random proxy', proxies)
        page_url = self.base_page_url.format(num)
        try:
            response = requests.get(page_url,headers=self.headers)
            if response.status_code == 200:
                pageHtml = response.text
                print('请求成功：url = {}, status_code = {}'.format(page_url, response.status_code))
                return pageHtml
            else:
                print('请求错误：url = {}, status_code = {}'.format(page_url,response.status_code))
                print(response.text)
                return None
        except Exception as e:
            print('请求异常：url = {}, error = {}'.format(page_url,e))
            print(response.text)
            return None
    # 获取详首页电影的 top_no movie_url,返回一个列表
    def myList(self,pageHtml):
        # 书写正则表达式
         pattern = re.compile(r'<div class="pic">.*?<a title="(.*?)" href="(.*?)" .*?>.*?<div class="info">.*?<li>.*?class="rating(.*?)-t">.*?class="date">.*?</span>.*?(.*?)</div>', re.S)
         movieInfoList = re.findall(pattern,pageHtml)
         print(movieInfoList)
         return movieInfoList
    # 获取电影信息源码
    def myHtml(self,movie_url):
        try:
            response = requests.get(movie_url,headers=self.headers)
            if response.status_code == 200:
                moviePageHtml = response.text
                return  moviePageHtml
            else:
                print('请求错误：url = {}, status_code = {}'.format(movie_url,response.status_code))
                return None
        except Exception as e:
            print('请求异常：url = {}, error = {}'.format(movie_url,e))
    # 获取电影的详细信息
    def movieDetails(self,movieHtml):

        pattern = re.compile(r'<div id="content">.*?<h1>.*?>(.*?)</span>.*? rel="v:directedBy">(.*?)</a>.*?<span class="pl".*?</span>(.*?)<br/>.*?<span class="pl">制片国家.*?<strong class="ll rating_num" property="v:average">(.*?)</strong>.*?<span property="v:votes">(.*?)</span>',re.S)
        movie_data = re.findall(pattern,str(movieHtml))
        # 测试输出
        print(movie_data)
        if movie_data is None:
            return None
        return movie_data
        # 保存到数据库中

if __name__ == '__main__':
    dbObj = DouBan()
    Tool = DataTool()
    xcl =Excel()
    # row = 1 是为了保存到Excel中 做的处理
    row = 1
    pool = Pool(8)
    for i in range(0,10):
      if i%15 == 0:
        pageHtml = dbObj.startCrawl(i)
        # print(pageHtml)
        urlsList = dbObj.myList(pageHtml)
        #pool.map(dbObj.myList, pageHtml)
        for eachUrl in urlsList:
            #movieHtml=pool.map(dbObj.myHtml,urlsList)
            #print('List sss')
            movieHtml = dbObj.myHtml(eachUrl[1])
            eachDetail = dbObj.movieDetails(movieHtml)
            rate = int(eachUrl[2])
            comment = eachUrl[3]
            #eachDetail=pool.map(dbObj.movieDetails, movieHtml)
            print(eachDetail)
            for movieTuple in eachDetail:
                newData = Tool.newTupleData(movieTuple,rate,comment)
                xcl.write_data(row,newData)
                row += 1
                print(newData)
                pool.close()
                pool.join()
    xcl.saveExcelData()
end =time.time()
print('Cost time:',end-start)