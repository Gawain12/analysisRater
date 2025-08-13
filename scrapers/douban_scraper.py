import asyncio
import os
import random
import re
import time
import urllib.parse
import sys
import csv
from typing import Union

# Add parent directory to path to allow importing 'config'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiohttp
import pandas as pd
from tqdm.asyncio import tqdm

# ==============================================================================
# Part 1: Web Parsing Logic (formerly web_parser.py)
# ==============================================================================

BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

async def fetch_imdb_id_from_web(session: aiohttp.ClientSession, douban_url: str, retries=3) -> Union[str, None]:
    """
    Asynchronously fetches a Douban movie page and parses the IMDB ID from its HTML content.
    Includes a retry mechanism for network errors.
    """
    if not douban_url:
        return None
    
    print(f"  - [Web Fetch] Cache miss, fetching IMDB ID from: {douban_url}")
    headers = {'User-Agent': BROWSER_USER_AGENT}
    
    for attempt in range(retries):
        await asyncio.sleep(random.uniform(0.5, 1.5))
        try:
            async with session.get(douban_url, headers=headers, verify_ssl=False, timeout=30) as response:
                if response.status == 404:
                    # Don't retry on a 404, the page simply doesn't exist.
                    # print(f"⚠️ Page not found (404) for URL: {douban_url}")
                    return None
                response.raise_for_status()
                html_content = await response.text()
                imdb_match = re.search(r'IMDb:</span>\s*(tt\d+)', html_content)
                if imdb_match:
                    return imdb_match.group(1)
                return None # Page loaded but no IMDb ID, no need to retry
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"❌ Web fetch failed (URL={douban_url}, attempt {attempt + 1}/{retries}): {e}")
            if attempt + 1 == retries:
                print(f"❌ Max retries reached, giving up on {douban_url}")
                return None
            await asyncio.sleep(3) # Wait before the next retry
    return None

# ==============================================================================
# Part 2: Main Scraper Application
# ==============================================================================

# --- 配置 ---
try:
    from config.config import DOUBAN_CONFIG
    DOUBAN_USER_ID = DOUBAN_CONFIG.get('user')
    if not DOUBAN_USER_ID:
        raise ValueError("Douban user ID ('user') not found in config.py")
except (ImportError, ValueError) as e:
    print(f"⚠️  Could not load user from config: {e}. Trying environment variable...")
    DOUBAN_USER_ID = os.environ.get('DOUBAN_USER')
    if not DOUBAN_USER_ID:
        DOUBAN_USER_ID = "shuaMovie"
        print(f"⚠️  Using default User ID: {DOUBAN_USER_ID}. Please configure it properly.")

# --- API ---
LIST_API_URL = f"https://m.douban.com/rexxar/api/v2/user/{DOUBAN_USER_ID}/interests"

# --- 缓存文件 ---
IMDB_CACHE_FILE = "db_imdb.csv"

def load_imdb_cache():
    """从缓存文件加载豆瓣ID到IMDB ID的映射。"""
    if not os.path.exists(IMDB_CACHE_FILE):
        return {}
    try:
        df = pd.read_csv(IMDB_CACHE_FILE, dtype={'id': str, 'imdb': str})
        if df.empty or not {'id', 'imdb'}.issubset(df.columns):
            return {}
        df.drop_duplicates(subset=['id'], keep='last', inplace=True)
        return pd.Series(df.imdb.values, index=df.id).to_dict()
    except (pd.errors.ParserError, pd.errors.EmptyDataError, KeyError) as e:
        print(f"⚠️ Cache file '{IMDB_CACHE_FILE}' is corrupted or invalid. Deleting it and starting fresh. Reason: {e}")
        try:
            os.remove(IMDB_CACHE_FILE)
        except OSError as remove_err:
            print(f"❌ Failed to delete corrupted cache file: {remove_err}")
        return {}

def save_new_cache_entries(new_entries: list):
    """Appends a list of new ID mappings to the cache file."""
    if not new_entries:
        return
    
    print(f"\n✍️  Appending {len(new_entries)} new entries to the IMDB cache file...")
    file_exists = os.path.exists(IMDB_CACHE_FILE)
    try:
        with open(IMDB_CACHE_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(IMDB_CACHE_FILE) == 0:
                writer.writerow(['id', 'imdb'])
            writer.writerows(new_entries)
    except IOError as e:
        print(f"❌ Error writing to cache file {IMDB_CACHE_FILE}: {e}")

# --- 数据处理 ---
def process_movie_data(interest_data):
    subject = interest_data.get('subject', {})
    my_rating = interest_data.get('rating', {})
    douban_id = subject.get('id')
    
    # Safely extract year from pubdate
    pubdates = subject.get('pubdate', [])
    pubdate = pubdates[0] if pubdates else ''
    year_match = re.search(r'(\d{4})', pubdate)
    year = year_match.group(1) if year_match else subject.get('year')

    processed = {
        'Const': None, # Placeholder for IMDB_ID, to be filled later
        'Your Rating': my_rating.get('value', 0) if my_rating else 0,
        'Date Rated': interest_data.get('create_time', '').split(' ')[0],
        'Title': subject.get('title'),
        'URL': f"https://movie.douban.com/subject/{douban_id}/",
        'Title Type': subject.get('type', 'movie'),
        'IMDb Rating': subject.get('rating', {}).get('value', 0), # This is Douban's rating
        'Runtime (mins)': subject.get('duration_in_seconds', 0) // 60,
        'Year': year,
        'Genres': ", ".join(subject.get('genres', [])),
        'Num Votes': subject.get('rating', {}).get('count', 0), # Douban's vote count
        'Release Date': pubdate,
        'Directors': ", ".join([d['name'] for d in subject.get('directors', [])]),
        # Extra fields from the new API that might be useful
        'MyComment': interest_data.get('comment', ''),
        'DoubanID': douban_id
    }
    return processed

# --- 异步网络请求 ---
async def fetch_movie_list_page(session, start_index, page_size=50, retries=3):
    params = {"type": "movie", "status": "done", "count": page_size, "start": start_index, "for_mobile": 1}
    headers = {'User-Agent': BROWSER_USER_AGENT, 'Referer': 'https://m.douban.com/'}

    for attempt in range(retries):
        await asyncio.sleep(random.uniform(1.0, 2.0))
        try:
            async with session.get(LIST_API_URL, headers=headers, params=params, verify_ssl=False, timeout=30) as r:
                r.raise_for_status()
                return await r.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"❌ List request failed (start={start_index}, attempt {attempt + 1}/{retries}): {e}")
            if attempt + 1 == retries:
                print(f"❌ Max retries reached, giving up on page start={start_index}")
                return None
            await asyncio.sleep(3) # Wait before the next retry
    return None

async def process_interest(session, interest, imdb_cache):
    processed_data = process_movie_data(interest)
    douban_id = processed_data.get('DoubanID')
    new_cache_entry = None

    if douban_id in imdb_cache:
        processed_data['Const'] = imdb_cache[douban_id]
    else:
        mobile_url = f"https://m.douban.com/movie/subject/{douban_id}/" if douban_id else None
        imdb_id = await fetch_imdb_id_from_web(session, mobile_url)
        if imdb_id:
            processed_data['Const'] = imdb_id
            if douban_id:
                imdb_cache[douban_id] = imdb_id
                new_cache_entry = (douban_id, imdb_id)
            
    return processed_data, new_cache_entry

async def main():
    start_time = time.time()
    print(f"🎬 开始为用户 {DOUBAN_USER_ID} 爬取已看电影列表...")
    output_filename = f"douban_{DOUBAN_USER_ID}_ratings.csv" # Changed output filename to match old pattern
    imdb_cache = load_imdb_cache()
    print(f"✅ 已从 '{IMDB_CACHE_FILE}' 加载 {len(imdb_cache)} 条缓存记录。")
    
    async with aiohttp.ClientSession() as session:
        print("🔍 正在获取电影总数...")
        initial_data = await fetch_movie_list_page(session, 0, 1)
        if not initial_data or 'total' not in initial_data:
            print("❌ 无法获取电影总数，脚本终止。"); return
        total_movies = initial_data['total']
        print(f"✅ 找到 {total_movies} 部已看电影。")

        print("\n🚀 步骤 1/2: 并发获取所有电影的基本信息...")
        list_tasks = [fetch_movie_list_page(session, i, 50) for i in range(0, total_movies, 50)]
        all_interests = []
        for f in tqdm(asyncio.as_completed(list_tasks), total=len(list_tasks), desc="获取基本信息"):
            page_data = await f
            if page_data and 'interests' in page_data:
                all_interests.extend(page_data['interests'])
        
        print(f"\n✅ 已获取 {len(all_interests)} 条基本电影记录。")
        print("\n🚀 步骤 2/2: 并发从缓存或网页获取IMDB_ID...")
        processing_tasks = [process_interest(session, interest, imdb_cache) for interest in all_interests]
        all_movies_data = []
        new_cache_entries = []
        for f in tqdm(asyncio.as_completed(processing_tasks), total=len(processing_tasks), desc="获取IMDB ID"):
            processed_data, new_cache_entry = await f
            if processed_data:
                all_movies_data.append(processed_data)
            if new_cache_entry:
                new_cache_entries.append(new_cache_entry)

    if new_cache_entries:
        save_new_cache_entries(new_cache_entries)

    if not all_movies_data:
        print("\n🤷 没有找到任何电影数据，无法生成CSV。"); return

    print(f"\n💾 正在将 {len(all_movies_data)} 条数据保存到 {output_filename}...")
    df = pd.DataFrame(all_movies_data)
    
    # Ensure columns match the desired final output, reordering and dropping extras
    final_columns = ['Const', 'Your Rating', 'Date Rated', 'Title', 'URL', 'Title Type', 
                     'IMDb Rating', 'Runtime (mins)', 'Year', 'Genres', 'Num Votes', 
                     'Release Date', 'Directors', 'MyComment']
    
    # Add missing columns with default values if they don't exist
    for col in final_columns:
        if col not in df.columns:
            df[col] = None
            
    df = df[final_columns] # Reorder and select final columns
    
    df.sort_values(by='Date Rated', ascending=False, inplace=True)
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    end_time = time.time()
    print("\n🎉 任务完成！")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"数据已保存在: {output_filename}")


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 用户手动终止了脚本。")
