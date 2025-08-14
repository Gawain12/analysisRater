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

# --- Scraper Configurations ---
# INSTRUCTIONS:
# 1. Open your browser's developer tools (F12).
# 2. Go to the Network tab.
# 3. Visit your Douban or IMDb ratings page.
# 4. Find a relevant request (e.g., 'interests' for Douban, 'graphql' for IMDb).
# 5. Right-click the request, choose "Copy as cURL", and paste it into a text editor.
# 6. Copy the 'Cookie' string and paste it into the 'cookie' field below for the respective site.
# Douban Scraper Configuration
DOUBAN_CONFIG = {
    'user': 'gawaint',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://m.douban.com/',
        'Cookie': 'bid=lbDPxIrjxUI; viewed="1394604"; ll="118318"; _vwo_uuid_v2=D24ACC2BB95F5671CA208D1A278A70003|433740619214b024a00c9e776946b255; push_noty_num=0; push_doumail_num=0; _pk_id.100001.4cf6=aa21d2bdb42164d2.1752046919.; dbcl2="153341182:j0+bbgIPa90"; _ga_Y4GN1R87RG=GS2.1.s1754708596$o2$g0$t1754708596$j60$l0$h0; _ga=GA1.2.484727185.1754675904; __yadk_uid=DsYfgaBlBYfi0kLE39mzWqdsSVQH1Q61; __utmv=30149280.15334; ck=Flp2; __utmc=30149280; __utmc=223695111; frodotk_db="2a715bf74b4e22927f5413e5e1ea67b6"; ct=y; __utmz=30149280.1755112494.13.3.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmz=223695111.1755115133.1144.628.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/search; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1755167543%2C%22https%3A%2F%2Fwww.douban.com%2Fsearch%3Fsource%3Dsuggest%26q%3D%E4%BB%8E%E6%B5%B7%E5%BA%95%22%5D; _pk_ses.100001.4cf6=1; __utma=30149280.484727185.1754675904.1755112494.1755167544.14; __utmb=30149280.0.10.1755167544; __utma=223695111.1788169032.1629456124.1755115133.1755167544.1145; __utmb=223695111.0.10.1755167544' # PASTE YOUR DOUBAN COOKIE HERE
    }
}

# IMDb Configuration
IMDB_CONFIG = {
    'user_id': 'ur79467081',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'ubid-main=133-5134666-5097059; uu=eyJpZCI6InV1YWVhZWU3NTM1OTE3NDBjZGJjOGIiLCJwcmVmZXJlbmNlcyI6eyJmaW5kX2luY2x1ZGVfYWR1bHQiOmZhbHNlfSwidWMiOiJ1cjc5NDY3MDgxIn0=; _cc_id=3bbfe8bfcb2c1db729b857abf8fff2f4; _au_1d=AU1D-0100-001743611697-8SLX3UGW-6BY7; _ga=GA1.1.2102819527.1743611733; _ga_FVWZ0RM4DH=GS1.1.1743638153.2.0.1743638153.60.0.0; __gads=ID=c409da0f77c68f06:T=1743611644:RT=1743872742:S=ALNI_MbCqFw4YaPTOx4IbTsV2e-4JVosag; __gpi=UID=00001086f93ad444:T=1743611644:RT=1743872742:S=ALNI_MbVPoMv5RHpZWqVGaC82yo6Yx3zsA; __eoi=ID=b2667cec344e1e82:T=1743611644:RT=1743872742:S=AA-AfjZJb28cBkQPEJswdfIlmHSw; session-id=133-9732400-6625435; ad-oo=0; as=%7B%22n%22%3A%7B%7D%7D; at-main=Atza|IwEBIHHAtNd2bfUfSJTnij6ieCS1WXSpSYZh7FGBNFw2UmC0PV5AvDXyulPUjagY2UkPLatTclX9Oe-YgrnEuNK4QkMQPgE1m2frScV4Td8zCcrtqE0kqQvASfT4cir7WRFWN_gk5FIyT1dRjrt7WQy7MAuCKbX6rf_0PR0BjdsVuuybM4OxrmQZr9YH2SNh06dlHXzU8eWUHtacwKZ3fZivHxENVtuSq-AN5XtYnHxY5xXhwg; sess-at-main=\"jtUwk8fpYXoqTyucAomDJoffMZJuZIKe0peOr5m86a0=\"; session-id-time=2082787201l; ci=eyJhY3QiOiJDUUVBdVlBUUVBdVlBRjRBQkNFTmZyLWdBQUFBQUFBQUFCYW1HNndCMkdvc05UNGF0aHJERFh1R3dZYkR3MlREWmVHMFlicUFBRUFBQUFBIiwiZ2N0IjoiQ1FFQXVZQVFFQXVZQUY0QUJDRU5BYkVnQU5MZ0FBQUFBQmFnSG1RUGdBRkFBTkFBeUFCd0FFRUFKQUFsQUJPQUNvQUZvQU1vQWFBQnFBRDBBSVVBUkFCR2dDWUFKd0FVQUFwQUJVQUM3QUdFQVlnQXpBQnVnRGtBT1lBZmdCQUFDRUFFUkFJNEFqd0JOQUNsQUZhQUxnQWFvQThRQi1nRVJBSXRBUndCSFFDVEFFdEFKd0FVMEFySUJYZ0RBZ0dLQU02QWNJQTRnQjFBRDlBSDhBUkFBalVCSG9DalFGaGdMekFYdUF3UUJsZ0R6QUFBZ0FBRkFvQU1BQVFmUUNRQVlBQWctZ09nQXdBQkI5QWxBQmdBQ0Q2QlNBREFBRUgwQXdBR0FBSVBvQ2dBTUFBUWZRR0FBWUFBZy1nUUFBd0FCQjlBUUFQQUJBQUNRQUZRQU5ZQXdnREVBR1lBT1lBZ0FCU2dEVkFKYUFWa0Fyd0J3Z0ZoZ0EuY0FBQUFBQUFBQUEiLCJwdXJwb3NlcyI6WyIxIiwiMiIsIjQiLCI3IiwiOSIsIjEwIiwiMTEiXSwidmVuZG9ycyI6WyI2OCIsIjc3IiwiNzU1IiwiNzkzIiwiODA0IiwiMTEyNiIsIjUwMDI1IiwiNTAwMzAiXSwiaXNHZHByIjp0cnVlfQ; x-main=1ggaaMJuMhDUB@zzFto2hnZr7L6fkxgpsPksPZaVFWU4wfI619fqXEan0jwP9V2I; session-token=6L4U7uy+ETCDFfbyymQS1ronOLkYnzUtU6Mdd8xD4fwIgfBBl+ArgYT1AlAFIQLHpsWZz33b03nxtDJPQe10joEoAknVc6vZXsFO/wjTWF++emely+QFUgcOtlacba9f2Xk7EGpilklL8sAkYBOrkkFUuvSrkk++iewcxUxW+BeSdJVcd5GGAvwH+0Y2IAO7uwCu4eSIUaUmkqyOkSRykhlzdlSORTm8ROhC7s1jyZv2exOESaQyTMnXfuNtH48pwNO+h0h56h95BTe+SRfaK60McW0+CSM/wSikkp9OjX0EcNibGoa+432s9vedj11lkw41g7KdomXbuiNQ9g3Y382MKbbNL5OOrJYOSYBZkTujmbffukWgkuAzwDrVV7YQ' # PASTE YOUR IMDB COOKIE HERE
    }
}

# File Paths
FILE_PATHS = {
    'output_csv': 'web/{}_movie_list.csv'
}
