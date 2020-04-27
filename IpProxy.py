import requests

def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    proxypool_url = 'http://127.0.0.1:3128'
    return requests.get(proxypool_url).text.strip()

proxies = {'https' : get_random_proxy()}
print('get random proxy', proxies)
try:
    res = requests.get('http://httpbin.org/get',proxies=proxies)
    print(res.text)
except requests.exceptions.ConnectionError as e:
    print('Error',e.args)