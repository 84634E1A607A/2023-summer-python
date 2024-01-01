import requests
import sqlite3
import json
from Constants import Constants
import time
import datetime

APIURL = 'https://interface.sina.cn/pc_api/public_news_data.d.json?mod=pctech&cids=40809%2C240707&editLevel=0%2C1%2C2%2C3%2C4%2C6%2C7&statics=1&up={up}&down=0'
CSDAPIURL = 'https://interface.sina.cn/pc_api/public_news_data.d.json?cids=294935%2C294936&pdps=&smartFlow=&editLevel=0%2C1%2C2%2C3%2C4%2C6%2C97%2C98%2C99&mod=&type=std_news%2Cstd_slide%2Cstd_video&pageSize=20&cTime=1677421260&up={up}&action=1'
ROLLINGAPIURL = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=372&lid=2431&k=&num=50&page={page}'
CSJAPIURL = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=402&lid=2559&num=20&versionNumber=1.2.8&page={page}&encode=utf-8'
LAPTOPAPIURL = 'https://feed.sina.com.cn/api/roll/get?pageid=302&lid=1718&num=30&versionNumber=1.2.4&page={page}&encode=utf-8'
CAMERAAPIURL = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=49&lid=734&num=30&versionNumber=1.2.4&page={page}&encode=utf-8'
SQAPIURL = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=128&lid=1386&num=8&page={page}'
APPLEAPIURL = 'https://feed.sina.com.cn/api/roll/get?pageid=216&lid=1817&num=30&versionNumber=1.2.4&page={page}&encode=utf-8'
IPHONEAPIURL = 'https://feed.sina.com.cn/api/roll/get?pageid=217&lid=1810&num=50&versionNumber=1.2.4&ctime={starttime}&encode=utf-8'

dbconn = sqlite3.connect('newsInfo.db')

dbconn.execute('''\
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    docid TEXT UNIQUE NOT NULL,
    author TEXT,
    tags TEXT,
    title TEXT,
    stitle TEXT,
    url TEXT,
    created_at INTEGER,
    summary TEXT,
    media_name TEXT,
    thumbnail TEXT,
    comment_count INTEGER,
    comments_downloaded INTEGER DEFAULT 0,
    content_downloaded INTEGER DEFAULT 0,
    content_download_error INTEGER,
    words_extracted INTEGER DEFAULT 0,
    comments_extracted INTEGER DEFAULT 0,
    keywords TEXT
)
''')

def getNewsList(up: int, ApiUrl: str = APIURL) -> int:
    resp = requests.get(ApiUrl.format(up=up), headers={
        'User-Agent': Constants.GetRandomUserAgent()
    })

    resp.raise_for_status()

    data = json.loads(resp.text)
    if data['status']['code'] != 0:
        raise Exception('Failed to get news list!')
    
    items_inserted = 0

    if data['data'] is None:
        return 0

    for item in data['data']:
        # Escape double quotes
        if item['title'] is not None:
            item['title'] = item['title'].replace('"', '""')

        if item['stitle'] is not None:
            item['stitle'] = item['stitle'].replace('"', '""')

        if item['summary'] is not None:
            item['summary'] = item['summary'].replace('"', '""')

        cursor = dbconn.execute(f'''\
INSERT OR IGNORE INTO news (docid, author, tags, title, stitle, url, created_at, summary, media_name, thumbnail, comment_count)
VALUES (
    "{item['docid']}",
    "{item['author']}",
    "{','.join(item['tags'])}",
    "{item['title']}",
    "{item['stitle']}",
    "{item['url']}",
    "{item['ctime']}",
    "{item['summary']}",
    "{item['media']}",
    "{item['thumb']}",
    "{item['comment_count']}")
''')
        if cursor.rowcount > 0:
            items_inserted += 1
            print(f'DB: Inserted {item["title"]}')
        else:
            print(f'DB: Skipped {item["title"]}')

    dbconn.commit()
    return items_inserted

def GetRollingNewsList(page: int, ApiUrl: str = ROLLINGAPIURL) -> int:
    # Replace this with other APIs to crawl other news categories
    resp = requests.get(ApiUrl.format(page=page), headers={
        'User-Agent': Constants.GetRandomUserAgent()
    })

    resp.raise_for_status()

    data = json.loads(resp.text)

    if data['result']['status']['code'] != 0:
        raise Exception('Failed to get news list!')
    
    items_inserted = 0

    if data['result']['data'] is None or len(data['result']['data']) == 0:
        return -1
    
    for item in data['result']['data']:
        # Escape double quotes
        if item['title'] is not None:
            item['title'] = item['title'].replace('"', '""')

        if item['stitle'] is not None:
            item['stitle'] = item['stitle'].replace('"', '""')

        if item['intro'] is not None:
            item['intro'] = item['intro'].replace('"', '""')

        # Docid in this API is prefixed with "comos:"
        item['docid'] = item['docid'].split(":")[1]

        cursor = dbconn.execute(f'''\
INSERT OR IGNORE INTO news (docid, title, stitle, url, created_at, summary, media_name)
VALUES (
    "{item['docid']}",
    "{item['title']}",
    "{item['stitle']}",
    "{item['url']}",
    "{item['ctime']}",
    "{item['intro']}",
    "{item['media_name']}")
''')
        if cursor.rowcount > 0:
            items_inserted += 1
            print(f'DB: Inserted {item["title"]}')
        else:
            print(f'DB: Skipped {item["title"]}')
    
    dbconn.commit()
    return items_inserted

def GetTimelineNewsList(startTime: int, ApiUrl: str = IPHONEAPIURL) -> (int, int):
    # Replace this with other APIs to crawl other news categories
    resp = requests.get(ApiUrl.format(starttime=startTime), headers={
        'User-Agent': Constants.GetRandomUserAgent()
    })

    resp.raise_for_status()

    data = json.loads(resp.text)

    if data['result']['status']['code'] != 0:
        raise Exception('Failed to get news list!')
    
    items_inserted = 0

    if data['result']['data'] is None or len(data['result']['data']) == 0:
        return (-1, startTime)
    
    for item in data['result']['data']:
        # Escape double quotes
        if item['title'] is not None:
            item['title'] = item['title'].replace('"', '""')

        if item['stitle'] is not None:
            item['stitle'] = item['stitle'].replace('"', '""')

        if item['intro'] is not None:
            item['intro'] = item['intro'].replace('"', '""')

        # Docid in this API is prefixed with "comos:"
        item['docid'] = item['docid'].split(":")[1]

        cursor = dbconn.execute(f'''\
INSERT OR IGNORE INTO news (docid, title, stitle, url, created_at, summary, media_name)
VALUES (
    "{item['docid']}",
    "{item['title']}",
    "{item['stitle']}",
    "{item['url']}",
    "{item['ctime']}",
    "{item['intro']}",
    "{item['media_name']}")
''')
        if cursor.rowcount > 0:
            items_inserted += 1
            print(f'DB: Inserted {item["title"]}')
        else:
            print(f'DB: Skipped {item["title"]}')
    
    dbconn.commit()
    return (items_inserted, int(data['result']['end']))

def main():
    while True:
        print('Checking for new items...')
        for page in range(500):
            new_items = getNewsList(page)
            # new_items = getNewsList(page, CSDAPIURL)
            if new_items == 0:
                print('No new items, waiting for updates...')
                break

            print(f'Inserted {new_items} new items, waiting for a while...')
            time.sleep(1)
        
        # Wait for 10 minutes for some new items to pop up
        time.sleep(600)

def main2():
    for page in range(1, 2500):
        try:
            new_items = GetRollingNewsList(page)
            # new_items = GetRollingNewsList(page, APPLEAPIURL)
        except Exception as e:
            print(f'Failed to get news list at page {page}: {e}')
            raise e

        # We use new_items == -1 for the first time to crawl all items and <= 0 for the rest
        if new_items <= 0:
            print('No new items.')
            break

        time.sleep(1)

def main3():
    startTime = int(datetime.datetime.now().timestamp())
    while startTime > 0:
        try:
            (new_items, startTime) = GetTimelineNewsList(startTime)
        except Exception as e:
            print(f'Failed to get news list earlier than {startTime}: {e}')
            raise e

        # We use new_items == -1 for the first time to crawl all items and <= 0 for the rest
        if new_items <= 0:
            print('No new items.')
            break

        time.sleep(0.3)

if __name__ == '__main__':
    # main()
    # main2()
    main3()

dbconn.close()