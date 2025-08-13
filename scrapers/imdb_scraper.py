import requests
import csv
import time
import json
import os
import re
import sys 
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import IMDB_CONFIG

class CurlParser:
    """一个用于解析cURL命令字符串以提取关键信息的工具类。"""
    @staticmethod
    def parse(curl_string):
        headers = {};
        try:
            curl_string = curl_string.replace('^', '').replace('\\\n', ' ').replace('`\n', ' ')
            header_matches = re.findall(r"-H '([^']*)'|--header '([^']*)'|\-H \"([^\"]*)\"", curl_string)
            for header_line in [next(item for item in match if item) for match in header_matches]:
                if ':' in header_line: key, value = header_line.split(':', 1); headers[key.strip().lower()] = value.strip()
            cookie_match = re.search(r"--cookie '([^']*)'|--cookie \"([^\"]*)\"", curl_string)
            if cookie_match: headers['cookie'] = next(c for c in cookie_match.groups() if c)
            if 'cookie' not in headers: raise ValueError("cURL命令中缺少关键的 'cookie' 信息。")
            return headers
        except Exception as e: print(f"❌ cURL解析失败: {e}"); return None

class IMDbRatingsScraper:
    """
    通过交叉获取移动端API和网页端数据，全面、高效地抓取IMDb用户评分。
    V-Final-Incremental: 支持增量更新，极大提升后续运行速度。
    """
    AUTH_FILE = 'auth.json'; CURL_FILE = 'curl_command.txt'
    EXPORT_FILENAME = 'imdb_ratings_export.csv'

    def __init__(self):
        self.user_id = IMDB_CONFIG.get('user_id')
        if not self.user_id: raise ValueError("IMDB_CONFIG中的'user_id'未设置。")
        self.api_base_url = "https://api.graphql.imdb.com/"
        self.web_base_url = f"https://www.imdb.com/user/{self.user_id}/ratings"
        self.session = requests.Session()
        
        self.api_headers = self._authenticate()
        self.web_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def _authenticate(self):
        # (Authentication logic is unchanged)
        if os.path.exists(self.AUTH_FILE):
            try:
                with open(self.AUTH_FILE, 'r', encoding='utf-8') as f: headers = json.load(f)
                print("✅ 已从 `auth.json` 文件成功加载认证信息。")
                return headers
            except (json.JSONDecodeError, KeyError): print(f"⚠️ `{self.AUTH_FILE}` 文件已损坏...")
        if os.path.exists(self.CURL_FILE) and os.path.getsize(self.CURL_FILE) > 0:
            print(f"ℹ️ 检测到 `{self.CURL_FILE}` 文件，正在尝试解析...")
            with open(self.CURL_FILE, 'r', encoding='utf-8') as f: curl_string = f.read()
            headers = CurlParser.parse(curl_string)
            if headers:
                with open(self.AUTH_FILE, 'w', encoding='utf-8') as f: json.dump(headers, f, indent=2)
                processed_filename = f"{self.CURL_FILE}.processed_on_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.CURL_FILE, processed_filename)
                print("\n✅ 解析成功！认证信息已保存至 `auth.json`。")
                return headers
            else: raise SystemExit("❌ 解析失败。")
        else:
            print("\n" + "="*60 + "\n⚙️ 首次运行或需要重新认证。")
            with open(self.CURL_FILE, 'w') as f: pass
            print(f"💡 我已在当前目录下创建了一个文件: '{self.CURL_FILE}'")
            print(f"   请将获取的cURL命令【粘贴到 '{self.CURL_FILE}' 文件中并保存】，然后【重新运行】此脚本。")
            raise SystemExit("="*60)

    def _fetch_api_page(self, cursor):
        # (Unchanged)
        payload = {"operationName": "userRatings", "variables": {"first": 250},"extensions": {"persistedQuery": {"version": 1, "sha256Hash": "ebf2387fd2ba45d62fc54ed2ffe3940086af52e700a1b3929a099d5fce23330a"}}}
        if cursor: payload['variables']['after'] = cursor
        try:
            response = self.session.post(self.api_base_url, json=payload, headers=self.api_headers, timeout=30)
            response.raise_for_status(); return response.json()
        except requests.RequestException as e: print(f"❌ API请求失败: {e}"); return None

    def _fetch_web_page(self, page_num):
        # (Unchanged)
        url = f"{self.web_base_url}?sort=date_added,desc&page={page_num}"
        try:
            response = self.session.get(url, headers=self.web_headers, timeout=30)
            response.raise_for_status(); return response.text
        except requests.RequestException as e: print(f"❌ 网页请求失败: {e}"); return None

    def _parse_movie_details_from_node(self, node):
        # (Unchanged, already safe and rich)
        details = {}; title_info = node.get('title', {}) or {}
        details['imdb_id'] = title_info.get('id');
        if not details['imdb_id']: return None
        details['title'] = (title_info.get('titleText', {}) or {}).get('text'); details['year'] = (title_info.get('releaseYear', {}) or {}).get('year')
        details['title_type'] = (title_info.get('titleType', {}) or {}).get('text')
        release_date_obj = title_info.get('releaseDate', {}) or {}
        if all(k in release_date_obj for k in ['year', 'month', 'day']):
            try: details['release_date'] = f"{release_date_obj['year']}-{str(release_date_obj['month']).zfill(2)}-{str(release_date_obj['day']).zfill(2)}"
            except TypeError: details['release_date'] = None
        else: details['release_date'] = None
        ratings_summary = title_info.get('ratingsSummary', {}) or {}; details['imdb_rating'] = ratings_summary.get('aggregateRating'); details['imdb_votes'] = ratings_summary.get('voteCount')
        runtime = title_info.get('runtime', {}) or {}; details['runtime_minutes'] = (runtime.get('seconds', 0) or 0) // 60
        details['genres'] = ', '.join([g.get('genre', {}).get('text', '') for g in (title_info.get('titleGenres', {}) or {}).get('genres', []) or []])
        credits_list = title_info.get('principalCredits', []) or []; directors = []
        for credit_category in credits_list:
            if (credit_category.get('category', {}) or {}).get('id') == 'director':
                directors.extend([(c.get('name', {}) or {}).get('nameText', {}).get('text', '') for c in credit_category.get('credits', []) or []])
        details['director'] = ', '.join(directors)
        return details

    def scrape_interleaved(self, existing_rating_ids=None):
        """以交叉模式抓取并合并数据，支持增量更新。"""
        if existing_rating_ids is None: existing_rating_ids = set()
        print(f"\n🚀 开始抓取数据... (模式: {'增量更新' if existing_rating_ids else '首次完整扫描'})")
        
        newly_scraped_movies = []
        stop_scraping = False
        page_num, api_cursor, web_page = 1, None, 1; api_done, web_done = False, False

        while not stop_scraping and not (api_done and web_done):
            print(f"\n--- 正在处理第 {page_num} 页 ---")
            
            personal_data_map_page = {}
            if not api_done:
                print("  - [API]  正在请求您的个人评分...")
                # ... (API logic, unchanged)
                api_data = self._fetch_api_page(api_cursor)
                if api_data and not api_data.get("errors"):
                    ratings_data = api_data.get('data', {}).get('userRatings')
                    if ratings_data and ratings_data.get('edges'):
                        edges = ratings_data.get('edges', [])
                        for edge in edges:
                            node = edge.get('node', {}); imdb_id = node.get('title', {}).get('id')
                            if not imdb_id: continue
                            ur = node.get('userRating', {})
                            rating_date_raw = ur.get('date')
                            personal_data_map_page[imdb_id] = {
                                'my_rating': ur.get('value'),
                                'rating_date': datetime.fromisoformat(rating_date_raw.replace('Z', '+00:00')).strftime('%Y-%m-%d') if rating_date_raw else None
                            }
                        print(f"  - [API]  已获取 {len(edges)} 条个人评分数据。")
                        page_info = ratings_data.get('pageInfo', {}); api_cursor = page_info.get('endCursor')
                        if not page_info.get('hasNextPage', False): api_done = True; print("  - [API]  您的所有个人评分已获取完毕。")
                    else: api_done = True; print("  - [API]  未找到更多评分数据。")
                else: api_done = True; print(f"  - [API]  请求失败或返回错误。")

            if not web_done and not stop_scraping:
                print("  - [Web]  正在批量获取电影公开详情...")
                # ... (Web logic, unchanged)
                html_content = self._fetch_web_page(web_page)
                if html_content:
                    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html_content, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1)); search_results = data['props']['pageProps']['mainColumnData']['advancedTitleSearch']
                        movies_on_page = [self._parse_movie_details_from_node(edge.get('node', {})) for edge in search_results.get('edges', [])]
                        movies_on_page = [m for m in movies_on_page if m]
                        
                        movies_to_add_this_page = []
                        for movie in movies_on_page:
                            # --- 增量更新核心逻辑 ---
                            if movie['imdb_id'] in existing_rating_ids:
                                print(f"  - [INC]  发现已存在的电影 '{movie['title']}' (ID: {movie['imdb_id']})。停止扫描。")
                                stop_scraping = True
                                break # 停止处理本页的后续电影
                            
                            if movie['imdb_id'] in personal_data_map_page:
                                movie.update(personal_data_map_page[movie['imdb_id']])
                            movies_to_add_this_page.append(movie)
                        
                        newly_scraped_movies.extend(movies_to_add_this_page)
                        print(f"  - [Merge] 本页新增了 {len(movies_to_add_this_page)} 条记录。")
                        
                        if not search_results.get('pageInfo', {}).get('hasNextPage', False): web_done = True; print("  - [Web]  所有公开电影页面已获取完毕。")
                    else: web_done = True; print("  - [Web]  页面结构变化，未找到 __NEXT_DATA__。")
                else: web_done = True; print("  - [Web]  请求失败。")
            
            page_num += 1; web_page += 1
            if not stop_scraping and not (api_done and web_done): time.sleep(1.0)
        
        return newly_scraped_movies


def main():
    start_time = time.time()
    print("="*60 + "\n" + " IMDb 评分导出工具 V-Final (增量更新)".center(66) + "\n" + "="*60)
    try:
        scraper = IMDbRatingsScraper()
        
        # Define the output path in the parent directory
        output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f"imdb_{scraper.user_id}_ratings.csv")
        
        # Step 1: Load existing data for incremental update
        existing_movies = []
        existing_rating_ids = set()
        if os.path.exists(output_filename):
            try:
                with open(output_filename, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        existing_movies.append(row)
                        if row.get('Const'):
                            existing_rating_ids.add(row['Const'])
                print(f"✅ 成功加载了 {len(existing_movies)} 条已存在的记录。")
            except Exception as e:
                print(f"⚠️ 读取现有CSV文件 '{output_filename}' 时出错: {e}。将执行完整扫描。")

        # Step 2: Run the scraper with the set of existing IDs
        newly_scraped_movies = scraper.scrape_interleaved(existing_rating_ids)
        
        # Step 3: Save results
        if newly_scraped_movies:
            print(f"\n✅ 增量更新完成，共找到 {len(newly_scraped_movies)} 条新记录。")
            
            export_fieldnames = ['Const', 'Your Rating', 'Date Rated', 'Title', 'URL', 'Title Type', 'IMDb Rating', 'Runtime (mins)', 'Year', 'Genres', 'Num Votes', 'Release Date', 'Directors']
            
            # Convert newly scraped data to the export format
            new_export_data = []
            for movie in newly_scraped_movies:
                new_export_data.append({
                    'Const': movie.get('imdb_id'), 'Your Rating': movie.get('my_rating'), 'Date Rated': movie.get('rating_date'),
                    'Title': movie.get('title'), 'URL': f"https://www.imdb.com/title/{movie.get('imdb_id')}/",
                    'Title Type': movie.get('title_type'), 'IMDb Rating': movie.get('imdb_rating'), 'Runtime (mins)': movie.get('runtime_minutes'),
                    'Year': movie.get('year'), 'Genres': movie.get('genres'), 'Num Votes': movie.get('imdb_votes'),
                    'Release Date': movie.get('release_date'), 'Directors': movie.get('director')
                })
            
            # Combine new data with existing data (newest first)
            combined_data = new_export_data + existing_movies
            
            with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=export_fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(combined_data)
            print(f"🎉 完美！已将 {len(combined_data)} 条完整记录以标准格式保存到文件: {output_filename}")
        else:
            print("\n✅ 您的数据已是最新，无需更新。")

    except SystemExit as e:
        print(f"\n脚本已终止: {e}")
    except Exception as e:
        import traceback; print(f"\n发生未知严重错误: {e}"); traceback.print_exc()
    finally:
        duration = time.time() - start_time
        if duration > 1.0:
            print("\n" + "="*60 + f"\n程序运行完毕，总耗时: {duration:.2f} 秒。\n" + "="*60)

if __name__ == "__main__":
    main()