import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import argparse
import sys
import os

# Add parent directory to path to allow importing 'config'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import DOUBAN_CONFIG

# ==============================================================================
# Part 1: 可重用的豆瓣 API 客户端
# ==============================================================================

class DoubanClient:
    """
    一个用于与豆瓣 Frodo API 交互的客户端。
    它会自动处理请求签名和固定的 API 参数。
    """
    _HMAC_KEY = "bf7dddc7c9cfe6f7"
    _API_KEY = "0dad551ec0f84ed02907ff5c42e8ec70"
    _FRODO_USER_AGENT = 'api-client/1 com.douban.frodo/7.25.0(213) Android/28 product/Pixel 3 vendor/Google model/Pixel 3 rom/android network/wifi platform/mobile nd/1'

    def __init__(self, timeout=20):
        """
        初始化客户端。
        :param timeout: 请求超时时间（秒）。
        """
        self.timeout = timeout
        self.headers = DOUBAN_CONFIG.get('headers', {})

        if not self.headers.get('Cookie'):
            raise SystemExit("❌ 配置错误: 请确保在 `config.py` 的 `DOUBAN_CONFIG` 中提供了 'Cookie'。")
        
        self.headers['User-Agent'] = self._FRODO_USER_AGENT
        print("✅ 已从 `config.py` 加载 Douban 认证信息。")

    def _get_signature(self, method: str, url: str) -> dict:
        """
        为给定的 URL 和方法计算签名。这是一个内部辅助方法。
        """
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        timestamp = str(int(time.time()))
        
        string_to_sign = f"{method.upper()}&{urllib.parse.quote(path, safe='')}&{timestamp}"

        hmac_sha1 = hmac.new(
            self._HMAC_KEY.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()

        sig_base64 = base64.b64encode(hmac_sha1).decode('utf-8')

        return {"_sig": sig_base64, "_ts": timestamp}

    def request(self, method: str, url: str, params: dict = None):
        """
        发起一个经过签名的 API 请求。
        这是客户端的核心功能。

        :param method: HTTP 方法 (例如 'GET', 'POST').
        :param url: 完整的请求 URL (不包含任何查询参数)。
        :param params: 一个包含业务特定查询参数的字典 (例如 {'q': 'keyword'}).
        :return: requests.Response 对象。
        """
        # 1. 准备业务参数 (如果未提供，则为空字典)
        request_params = params.copy() if params else {}

        # 2. 生成签名并合并固定的 API 参数
        signature_data = self._get_signature(method, url)
        request_params.update({
            "apikey": self._API_KEY,
            "_sig": signature_data['_sig'],
            "_ts": signature_data['_ts'],
        })

        # 3. 准备请求头 (从 __init__ 加载)
        headers = self.headers

        print(f"\n--- 准备发起 {method} 请求 ---")
        print(f"目标 URL: {url}")
        print(f"业务参数: {params or '{}'}")
        
        # 4. 发起请求
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=request_params,
                verify=False, # 在生产环境中请谨慎使用
                timeout=self.timeout
            )
            print("\n--- 收到响应 ---")
            print(f"请求的最终 URL: {response.url}")
            print(f"状态码: {response.status_code}")

            response.raise_for_status() # 如果状态码不是 2xx，则抛出异常
            print("\n✅ 请求成功！")
            return response

        except requests.exceptions.RequestException as e:
            print(f"\n❌ 请求失败！")
            if e.response is not None:
                print(f"状态码: {e.response.status_code}")
                # 尝试以 JSON 格式打印错误，否则打印原始文本
                try:
                    print(f"错误响应 (JSON): {e.response.json()}")
                except ValueError:
                    print(f"错误响应 (Raw): {e.response.text}")
            else:
                print(f"网络或请求错误: {e}")
            return None

    def get(self, url: str, params: dict = None):
        """对 request 方法的便捷封装，用于发起 GET 请求。"""
        return self.request('GET', url, params=params)

# ==============================================================================
# Part 2: 主程序入口和命令行驱动逻辑
# ==============================================================================

def main():
    """主执行函数，处理命令行输入并调用客户端。"""
    parser = argparse.ArgumentParser(
        description="一个灵活的豆瓣 API 客户端，可通过命令行调用不同接口。",
        epilog="示例: \n  python %(prog)s search tt5636668 \n  python %(prog)s movie 26752088",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("type", choices=['search', 'movie'], help="选择接口类型: 'search' (搜索) 或 'movie' (电影详情)。")
    parser.add_argument("value", help="传递给接口的值 (例如: 搜索词 'tt5636668' 或电影ID '26752088')。")
    args = parser.parse_args()

    # 初始化客户端
    client = DoubanClient()

    target_url = ""
    api_params = None

    # 根据参数构建 URL 和业务参数
    if args.type == 'search':
        print(f"🎬 任务: 【搜索】，关键词: {args.value}")
        target_url = "https://frodo.douban.com/api/v2/search/weixin"
        api_params = {"q": args.value} # 这是业务参数
    
    elif args.type == 'movie':
        print(f"🎬 任务: 【电影详情】，豆瓣ID: {args.value}")
        target_url = f"https://frodo.douban.com/api/v2/movie/{args.value}"
        # 此接口没有业务查询参数

    # 发起请求并处理响应
    if target_url:
        response = client.get(url=target_url, params=api_params)
        if response:
            print("\n--- 响应内容 ---")
            try:
                data = response.json()
                # If it's a search and the result is empty, provide a better message.
                if args.type == 'search' and data.get('total', 0) == 0:
                    print(f"⚠️  搜索成功，但未找到与 '{args.value}' 相关的结果。")
                    print("   这可能意味着：")
                    print("   1. 该条目不在豆瓣数据库中。")
                    print("   2. 您的 Cookie 可能已部分失效，导致搜索权限受限。")
                else:
                    # Print the full JSON if it's not an empty search result
                    import json
                    print(json.dumps(data, indent=2, ensure_ascii=False))
            except ValueError:
                # 如果不是 JSON，打印原始文本
                print(response.text)

if __name__ == "__main__":
    # 禁用 InsecureRequestWarning 警告
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main()
