import asyncio
import re
import socket
import ssl
import sys
import os
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import REDIS_CONFIG, DOUBAN_CONFIG
import requests
from fake_useragent import UserAgent
import aiohttp
import pandas as pd
import time
import redis




class DataTool(object):
    def newTupleData(self,originTupleData,comments,title,url,date,imdb_id):

        newDict = {}

        p3 = re.compile(r'</span>', re.S)
        p4 = re.compile(r'<span property=.*?>', re.S)
        p10 = re.compile(r'&#39;',re.S)

        # Corresponds to IMDB's 'Const'
        # Example: tt0000010
        newDict['IMDB_ID'] = imdb_id

        # Corresponds to IMDB's 'Your Rating'
        # Example: 8
        if 'rating' not in comments:
            rate = 0
        else:
            rate_match = re.search(r'rating(\d+)', comments)
            rate = int(rate_match.group(1)) if rate_match else 0
        newDict['YourRating'] = rate # Douban uses a 5-star system, we can multiply by 2 later if needed.

        # Corresponds to IMDB's 'Date Rated'
        # Example: 2022-07-24
        mydate_match = re.search(r'date">(\d{4}-\d{2}-\d{2})<', comments)
        newDict['DateRated'] = mydate_match.group(1) if mydate_match else ''

        # Corresponds to IMDB's 'Title'
        # Example: La sortie de l'usine Lumière à Lyon
        title = re.sub(p10, "'", title)
        newDict['Title'] = title

        # Corresponds to IMDB's 'URL'
        newDict['URL'] = url

        # Corresponds to IMDB's 'Title Type' - default to 'movie' for now
        newDict['TitleType'] = 'movie'

        if isinstance(originTupleData, tuple) and len(originTupleData) > 4:
            # Corresponds to IMDB's 'IMDb Rating'
            newDict['IMDbRating'] = float(originTupleData[3]) if originTupleData[3] else 0.0
            # Corresponds to IMDB's 'Num Votes'
            newDict['NumVotes'] = int(originTupleData[4]) if originTupleData[4] else 0
            # Corresponds to IMDB's 'Directors'
            newDict['Directors'] = originTupleData[1]
            # Corresponds to IMDB's 'Genres'
            gut = re.sub(p3, '', originTupleData[2])
            gut = re.sub(p4, '', gut)
            newDict['Genres'] = gut.replace('/', ', ')
        else:
            newDict['IMDbRating'] = 0.0
            newDict['NumVotes'] = 0
            newDict['Directors'] = ''
            newDict['Genres'] = ''

        # Corresponds to IMDB's 'Runtime (mins)' - Placeholder, requires new regex
        newDict['Runtime'] = 0
        # Corresponds to IMDB's 'Year' - Placeholder, requires new regex
        newDict['Year'] = 0
        # Corresponds to IMDB's 'Release Date' - comes from the main page list
        newDict['ReleaseDate'] = date
        # Douban specific field
        comment_match = re.search(r'comment">(.*?)<', comments)
        newDict['MyComment'] = comment_match.group(1) if comment_match else '还未评价'

        return newDict



class DouBan(object):
    def __init__(self,name):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.douban.com/',
            'Cookie': DOUBAN_CONFIG['cookie'],
            'Cache-Control': 'no-cache',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Priority': 'u=0, i',
            'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        self.basePageUrl = DOUBAN_CONFIG['base_url']
        self.name=name
        self.proxies=None
        self.all_movie_data = []
    def Num(self, retries=3, delay=5):
        pageUrl = self.basePageUrl.format(self.name, 0)
        for i in range(retries):
            try:
                response = requests.get(pageUrl, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    pageHtml = response.text
                    pattern = re.compile(
                        r'<div id="db-usr-profile">.*?<div class="info">.*?<h1>(.*?)看过的影视(.*?)</h1>.*?</div>',
                        re.S)
                    na = re.findall(pattern, pageHtml)
                    print(na)
                    if na:
                        nick = na[0][0]
                        num = int(na[0][1].strip('()'))
                        print('nickName is {}'.format(nick))
                        return nick, num
                    else:
                        return '没有', 3
                else:
                    print('请求错误：url = {}, status_code = {}'.format(pageUrl, response.status_code))
                    if i < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        sys.exit(0)
            except Exception as e:
                print('请求异常：url = {}, error = {}'.format(pageUrl, e))
                if i < retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    return None
        return None

    async def startCrawl(self,sem,session,num):
          await asyncio.sleep(random.uniform(3, 7))
          async with sem:
                try:
                    # print("Starting to Crawl %s" % num)
                    pageUrl = self.basePageUrl.format(self.name,num)
                    async with await session.get(pageUrl, headers=self.headers,ssl=ssl.create_default_context(),timeout=15) as response:
                            if response.status == 403:
                                print('请求错误：url = {}, status = {}'.format(pageUrl, response.status))
                                return await self.startCrawl(sem,session,num)
                            if response.status == 200:
                                # print('请求成功：url = {}, status = {}'.format(pageUrl, response.status))
                                responseText = await response.text()
                                # print("%s 爬取完毕......" % num )

                                return responseText
                            else:
                                print('请求错误：url = {}, status = {}'.format(pageUrl, response.status))
                                sys.exit(0)
                                return None
                except Exception as e:
                    print('请求异常：url = {}, error = {}'.format(pageUrl, e))
    # 获取详首页电影的movieUrl rate comment,返回一个列表

    async def myList(self,pageHtml,urlsLists, last_date):
        pattern = re.compile(r'<div class="item.*?">.*?<a href="(https?://movie\.douban\.com/subject/(\d+)/)".*?<em>(.*?)</em>.*?<li class="intro">(.*?)</li>(.*?)<li class="clearfix opt-ln">', re.S)
        movieInfoList = re.findall(pattern, pageHtml)
        if not movieInfoList:
           print("No movies found on this page. Check the regex and HTML structure.")
           with open("debug_page.html", "w", encoding="utf-8") as f:
               f.write(pageHtml)
           return True # Stop processing

        for movie_info in movieInfoList:
           # Extract the rating date from the last capture group
           rating_info = movie_info[4]
           mydate_match = re.search(r'date">(\d{4}-\d{2}-\d{2})<', rating_info)
           mydate = mydate_match.group(1) if mydate_match else None

           if mydate and mydate == last_date:
               print(f"Found last scraped movie with date {last_date}. Stopping.")
               return True # Stop processing

           # The release date is in the fourth group, but needs cleaning
           release_date_raw = movie_info[3]
           release_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', release_date_raw)
           release_date = release_date_match.group(1) if release_date_match else ''

           # Pass the full rating info string to be parsed later for comments and rating
           urlsLists.append((movie_info[0], movie_info[2], release_date, rating_info))

        return False # Continue processing


    async def myHtml(self,headers,sem,session,movieUrl,num=3):
         # print('try to request {}'.format(movieUrl))
         async with sem:
              try:
                    async with await session.get(movieUrl,headers=headers,ssl=ssl.create_default_context(),timeout=15) as response:
                        if response.status == 200:
                            responseText = await response.text()
                            #print(type(responseText))
                            return responseText

                        if response.status != 200:
                            with open("failed_urls.txt", "a") as f:
                                f.write(f"{movieUrl}\\n")
                            return str(response.status)
              except Exception as e:
                        print('请求异常：url = {}, error = {}'.format(movieUrl, e))
                        return 'no'

    # 获取电影的详细信息

    async def movieDetails(self,movieHtml,comment,title,url,date):
        if len(movieHtml)<100:
            newData = DataTool().newTupleData(movieHtml, comment, title, url,date, None)
            self.all_movie_data.append(newData)
            return

        pattern = re.compile(r'<div id="content">.*?<h1>.*?>(.*?)</span>.*? rel="v:directedBy">(.*?)</a>.*?<span class="pl".*?</span>(.*?)<br/>.*?<span class="pl">'
                             r'制片国家.*?<strong class="ll rating_num" property="v:average">(.*?)'
                             r'</strong>.*?<span property="v:votes">(.*?)</span>',re.S)

        movie_data = re.findall(pattern,str(movieHtml))

        pattern = re.compile(r'<div id="info">.*?<span class="pl">IMDb:</span>\s*(tt\d+)<br>', re.S)
        imdb_id_match = re.search(pattern, str(movieHtml))
        imdb_id = imdb_id_match.group(1) if imdb_id_match else None

        for movieTuple in movie_data:
            newData = DataTool().newTupleData(movieTuple, comment,title,url,date, imdb_id)
            if not newData.get('IMDB_ID'):
                print(f"Skipping movie '{title}' because no IMDb ID was found.")
                continue
            self.all_movie_data.append(newData)

        # 保存到数据库中
    async def download(self,sem,num,urlsLists, last_date):
        try:
            async with aiohttp.ClientSession() as session:
                    fhtml = await self.startCrawl(sem, session, num)
                    stop = await self.myList(fhtml,urlsLists, last_date)
                    return stop
        except Exception as e:
            print('Download error:', e)
            return True

    async def handle(self,sem,url,comment,title,date):
            async with aiohttp.ClientSession() as session:
                    html = await self.myHtml(self.headers,sem,session,url)
                    await self.movieDetails(html,comment,title,url,date)


def main(name, full_scrape=False):
    start = time.time()
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    dbObj = DouBan(name)
    print('This is %s doubanlist' % name)

    sem = asyncio.Semaphore(5)
    urlsLists = []
    
    last_date = None
    if not full_scrape:
        # In a real scenario, you might read the last date from the existing CSV
        pass
    print(f"Last scraped date: {last_date}")

    tasks = []

    print("Step 1: Getting user info and movie count...")
    nick,num=dbObj.Num()
    
    if num==0:
        print('NO DATA')
        return

    print("Step 2: Creating download tasks...")
    total_pages = (num + 14) // 15
    for i in range(min(2, total_pages)):
        task = asyncio.ensure_future(dbObj.download(sem, i * 15, urlsLists, last_date))
        tasks.append(task)
    loop = asyncio.get_event_loop()
    print("Step 3: Running download tasks...")
    loop.run_until_complete(asyncio.gather(*tasks))

    taskList = []
    print("Step 4: Creating handle tasks...")
    for eachUrl in urlsLists:
        comment = eachUrl[3]
        date=eachUrl[2]
        title=eachUrl[1]
        task = asyncio.ensure_future(dbObj.handle(sem, eachUrl[0], comment,title,date))
        taskList.append(task)
    loop = asyncio.get_event_loop()
    print("Step 5: Running handle tasks...")
    if taskList:
        loop.run_until_complete(asyncio.wait(taskList))
    
    # Save all collected data to CSV
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f"douban_{name}_ratings.csv")
    df = pd.DataFrame(dbObj.all_movie_data)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"Saved {len(df)} records to {output_filename}")

    end = time.time()
    print('Cost time:', end - start)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Douban movie scraper.')
    parser.add_argument('user', type=str, help='The Douban user ID to scrape.')
    parser.add_argument('--full-scrape', action='store_true', help='Perform a full scrape, ignoring previous data.')
    
    args = parser.parse_args()
    main(args.user, full_scrape=args.full_scrape)
