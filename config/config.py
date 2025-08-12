# config.py

# Database Configuration
DATABASE_CONFIG = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'port': '3306',
    'db_name': 'douban',
    'charset': 'UTF8MB4'
}

# Redis Configuration
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

# Douban Scraper Configuration
DOUBAN_CONFIG = {
    'base_url': 'https://movie.douban.com/people/{}/collect?start={}',
    'user_agents': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    ],
    'cookie': 'bid=lbDPxIrjxUI; viewed="1394604"; ll="118318"; _vwo_uuid_v2=D24ACC2BB95F5671CA208D1A278A70003|433740619214b024a00c9e776946b255; __yadk_uid=qpa3UfhtXRKzlq0Ds9UUFaE27DyasLQf; _pk_id.100001.8cb4=9dc6bd0f0096732e.1747882745.; push_noty_num=0; push_doumail_num=0; dbcl2="153341182:j0+bbgIPa90"; _ga_Y4GN1R87RG=GS2.1.s1754708596$o2$g0$t1754708596$j60$l0$h0; _ga=GA1.2.484727185.1754675904; __utmz=30149280.1754812021.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=30149280.15334; ck=Flp2; __utmc=30149280; frodotk_db="2a715bf74b4e22927f5413e5e1ea67b6"; ap_v=0,6.0; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1754978036%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_ses.100001.8cb4=1; __utma=30149280.484727185.1754675904.1754971825.1754978037.8; __utmt=1; __utmb=30149280.2.10.1754978037' # Add your Douban cookie here
}

# IMDB Configuration
IMDB_CONFIG = {
    'user_id': 'ur79467081',
    'cookie': '' # Add your IMDB cookie here
}

# File Paths
FILE_PATHS = {
    'output_csv': 'web/{}_movie_list.csv'
}
