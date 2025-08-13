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
    'user': 'gawaint',
    'base_url': 'https://movie.douban.com/people/{}/collect?start={}',
    'user_agents': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    ],
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
