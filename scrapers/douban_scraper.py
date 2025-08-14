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
    It uses the headers pre-configured in the session.
    """
    if not douban_url:
        return None
    
    # Do not print for validation call to keep output clean
    if "1298697" not in douban_url:
        print(f"  - [Web Fetch] Cache miss, fetching IMDB ID from: {douban_url}")
    
    for attempt in range(retries):
        await asyncio.sleep(random.uniform(0.5, 1.5))
        try:
            # The session now has the headers, so no need to pass them here.
            async with session.get(douban_url, verify_ssl=False, timeout=30) as response:
                if response.status == 404:
                    return None
                response.raise_for_status()
                html_content = await response.text()
                imdb_match = re.search(r'IMDb:</span>\s*(tt\d+)', html_content)
                if imdb_match:
                    return imdb_match.group(1)
                return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Suppress error for validation call, but show for others
            if "1298697" not in douban_url:
                print(f"❌ Web fetch failed (URL={douban_url}, attempt {attempt + 1}/{retries}): {e}")
            if attempt + 1 == retries and "1298697" not in douban_url:
                print(f"❌ Max retries reached, giving up on {douban_url}")
            await asyncio.sleep(3)
    return None

# ==============================================================================
# Part 2: Main Scraper Application
# ==============================================================================

# --- Configuration ---
from config.config import DOUBAN_CONFIG

DOUBAN_USER_ID = DOUBAN_CONFIG.get('user')
DOUBAN_HEADERS = DOUBAN_CONFIG.get('headers', {})

if not DOUBAN_USER_ID or not DOUBAN_HEADERS.get('Cookie'):
    raise SystemExit(
        "❌ 配置错误: 请确保在 `config.py` 的 `DOUBAN_CONFIG` 中提供了 'user' 和 'Cookie'。"
    )

print("✅ 已从 `config.py` 加载 Douban 认证信息。")


# --- API ---
LIST_API_URL = f"https://m.douban.com/rexxar/api/v2/user/{DOUBAN_USER_ID}/interests"

# --- Validation ---
async def validate_cookie(session):
    """
    Validates the Douban cookie by using the core 'fetch_imdb_id_from_web'
    function. This is the most reliable validation method as it directly
    tests the functionality that requires a valid session.
    """
    print("\n🔍 正在验证 Douban Cookie 的有效性...")
    test_douban_url = "https://m.douban.com/movie/subject/1298697/"
    validation_id = await fetch_imdb_id_from_web(session, test_douban_url)
    
    if validation_id:
        print(f"✅ Douban Cookie 验证通过 (获取到测试 ID: {validation_id})。")
        return True
    else:
        print("❌ Cookie 无效或已过期。无法获取测试页面的 IMDb ID。")
        return False

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

def save_imdb_cache(imdb_cache: dict):
    """Saves the entire ID cache to the file, overwriting it to ensure integrity."""
    if not imdb_cache:
        return
    
    print(f"\n✍️  Saving {len(imdb_cache)} total entries to the IMDB cache file (overwrite)...")
    try:
        # Convert dict to DataFrame and save, ensuring no duplicates and clean format
        df = pd.DataFrame(list(imdb_cache.items()), columns=['id', 'imdb'])
        df.drop_duplicates(subset=['id'], keep='last', inplace=True)
        df.to_csv(IMDB_CACHE_FILE, index=False, encoding='utf-8')
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

    for attempt in range(retries):
        await asyncio.sleep(random.uniform(1.0, 2.0))
        try:
            # The session is now initialized with headers, so we don't pass them here.
            async with session.get(LIST_API_URL, params=params, verify_ssl=False, timeout=30) as r:
                r.raise_for_status()
                return await r.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"❌ List request failed (start={start_index}, attempt {attempt + 1}/{retries}): {type(e).__name__} - {e}")
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
    output_filename = f"douban_{DOUBAN_USER_ID}_ratings.csv"
    imdb_cache = load_imdb_cache()
    print(f"✅ 已从 '{IMDB_CACHE_FILE}' 加载 {len(imdb_cache)} 条缓存记录。")

    # --- 增量更新逻辑: 加载已有数据 ---
    df_existing = pd.DataFrame()
    existing_ids = set()
    if os.path.exists(output_filename):
        try:
            cols = pd.read_csv(output_filename, nrows=0, encoding='utf-8-sig').columns.tolist()
            if 'DoubanID' not in cols:
                print(f"⚠️  '{output_filename}' is in an old format (missing 'DoubanID'). Deleting it to recreate.")
                os.remove(output_filename)
            else:
                df_existing = pd.read_csv(output_filename, dtype={'DoubanID': str}, encoding='utf-8-sig')
                if not df_existing.empty:
                    existing_ids = set(df_existing['DoubanID'].dropna().astype(str))
                    print(f"✅ 已从 '{output_filename}' 加载 {len(existing_ids)} 条已有电影记录，将进行增量更新。")
        except (pd.errors.EmptyDataError, FileNotFoundError):
            print(f"⚠️  '{output_filename}' 存在但为空或无法读取, 将重新创建。")
        except Exception as e:
            print(f"❌ Error processing existing ratings file '{output_filename}': {e}. Will try to recreate it.")
            try: os.remove(output_filename)
            except OSError as remove_err: print(f"❌ Failed to delete problematic file: {remove_err}")

    # Create a single session with the headers from config, to be used for all requests.
    async with aiohttp.ClientSession(headers=DOUBAN_HEADERS) as session:
        # --- Cookie Validation Step ---
        if not await validate_cookie(session):
            print("\n🛑 请根据 config.py 中的指引更新您的 Douban Cookie 后再试。")
            return

        # --- 智能增量获取逻辑 ---
        print("\n🚀 步骤 1/2: 智能增量获取最新的电影记录...")
        new_interests = []
        should_stop_fetching = False
        page_num = 0
        page_size = 50

        with tqdm(desc="增量获取页面", unit="page") as pbar:
            while not should_stop_fetching:
                page_data = await fetch_movie_list_page(session, page_num * page_size, page_size)
                pbar.update(1)

                if not page_data or 'interests' not in page_data or not page_data['interests']:
                    pbar.set_description("已到达末页")
                    break # Reached the end of the user's ratings

                interests_on_page = page_data['interests']
                
                for interest in interests_on_page:
                    douban_id = interest.get('subject', {}).get('id')
                    if douban_id in existing_ids:
                        pbar.set_description("发现重复记录,停止获取")
                        should_stop_fetching = True
                        break
                    else:
                        new_interests.append(interest)
                
                if should_stop_fetching:
                    break
                page_num += 1

        if not new_interests:
            print("\n✅ 数据已是最新，无需更新。")
            end_time = time.time()
            print(f"总耗时: {end_time - start_time:.2f} 秒")
            return
            
        print(f"\n✅ 发现 {len(new_interests)} 条新记录。")
        
        print("\n🚀 步骤 2/2: 并发从缓存或网页获取IMDB_ID (仅处理新电影)...")
        processing_tasks = [process_interest(session, interest, imdb_cache) for interest in new_interests]
        new_movies_data = []
        new_cache_entries = []
        for f in tqdm(asyncio.as_completed(processing_tasks), total=len(processing_tasks), desc="获取IMDB ID"):
            processed_data, new_cache_entry = await f
            if processed_data:
                new_movies_data.append(processed_data)
            if new_cache_entry:
                new_cache_entries.append(new_cache_entry)

    if new_cache_entries:
        save_imdb_cache(imdb_cache)

    df_new = pd.DataFrame(new_movies_data)
    
    # --- 增量更新逻辑: 合并数据 ---
    df_final = pd.concat([df_new, df_existing], ignore_index=True)

    print(f"\n💾 正在将 {len(df_final)} 条数据保存到 {output_filename}...")
    
    final_columns = ['Const', 'Your Rating', 'Date Rated', 'Title', 'URL', 'Title Type', 
                     'Douban Rating', 'Runtime (mins)', 'Year', 'Genres', 'Num Votes', 
                     'Release Date', 'Directors', 'MyComment', 'DoubanID']
    
    for col in final_columns:
        if col not in df_final.columns:
            df_final[col] = None
            
    df_final = df_final[final_columns]
    df_final.drop_duplicates(subset=['DoubanID'], keep='first', inplace=True)
    df_final.sort_values(by='Date Rated', ascending=False, inplace=True)
    
    df_final.to_csv(output_filename, index=False, encoding='utf-8-sig')

    end_time = time.time()
    print("\n🎉 任务完成！")
    print(f"新增 {len(df_new)} 条记录。")
    print(f"总记录数: {len(df_final)}。")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"数据已保存在: {output_filename}")


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 用户手动终止了脚本。")
