import sqlite3
import json
import requests
from Constants import Constants
import re
import datetime
import time
import random

dbconn = sqlite3.connect('newsInfo.db')

dbconn.execute('''\
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mid TEXT UNIQUE NOT NULL,
    docid TEXT NOT NULL,
    username TEXT,
    content TEXT,
    created_at INTEGER,
    raw_data TEXT,
    constraint fk_comments_docid foreign key (docid) references news (docid)
)
''')

APIURL = 'https://comment5.news.sina.com.cn/page/info?format=json&channel={channel}&newsid=comos-{docid}&page={page}&page_size=200'
ZhongCeSeqRe = re.compile(r'https?://zhongce.sina.com.cn/article/view/(\d+)')

delay_time = 0.5
last_delay_id = 0

def delay(id: any):
    global delay_time
    global last_delay_id
    if id != last_delay_id:
        delay_time = 0.5
        last_delay_id = id
    else:
        delay_time += 1

    time.sleep((random.random() + 0.1) * delay_time)

def DownloadComments(docid: str, url: str) -> None:
    id = docid
    if url.find("tech.sina.com.cn") != -1:
        channel = "kj"
    elif url.find("finance.sina.com.cn") != -1:
        channel = "cj"
    elif url.find("zhongce.sina.com.cn") != -1:
        channel = "kj"
        id = "zhongce_ugc_article_" + ZhongCeSeqRe.search(url).group(1)
    else:
        print("Unknown channel " + url)
        return

    total_count_veri = -1
    count = 0
    page = 1
    while True:
        # Previous loop not full
        if count % 100 != 0:
            break

        data = requests.get(APIURL.format(channel=channel, docid=id, page=page), headers={
            'User-Agent': Constants.GetRandomUserAgent()
        }).json()

        if data['result']['status']['code'] != 0:
            if data['result']['status']['code'] == 4:
                print(f'No comments for {docid}')
                dbconn.execute(f'UPDATE news SET comments_downloaded = 1 WHERE docid = "{docid}"')
                dbconn.commit()
                return

            print(f'Failed to get comments for {docid}:{page}!')
            return
        
        if data['result'].get('toplist') is not None:
            print(f'Mock data found, retrying, count={count}')
            delay(docid)
            continue

        if total_count_veri == -1:
            total_count_veri = data['result']['count']['show']
        else:
            if total_count_veri != data['result']['count']['show']:
                print(f'Comment count mismatch for {docid}, retrying')
                delay(docid)
                continue

        if len(data['result']['cmntlist']) == 0:
            break
        
        for comment in data['result']['cmntlist']:
            raw_data = json.dumps(comment).replace('"', '""')
            username = comment['nick'].replace('"', '""')
            content = comment['content'].replace('"', '""')
            mid = comment['mid']
            created_at = int(datetime.datetime.fromisoformat(comment['time']).timestamp())
            dbconn.execute(f'''\
INSERT OR IGNORE INTO comments (mid, docid, username, content, created_at, raw_data)
VALUES (
    "{mid}",
    "{docid}",
    "{username}",
    "{content}",
    "{created_at}",
    "{raw_data}"
)
''')
            count += 1

        page += 1

    dbconn.execute(f'UPDATE news SET comments_downloaded = 1 WHERE docid = "{docid}"')
    dbconn.commit()
    print(f'Downloaded {count} comments for {docid}')


def main():
    newsList = dbconn.execute('SELECT docid,url FROM news WHERE content_download_error IS NULL AND comments_downloaded = 0 -- ORDER BY comment_count DESC').fetchall()
    length = len(newsList)
    for index, news in enumerate(newsList):
        print(f'[{index + 1}/{length}] ', end="")
        try:
            DownloadComments(news[0], news[1])
        except Exception as e:
            print(f'Failed to download comments for {news[0]}: {e}')

        delay(index)
    

if __name__ == '__main__':
    main()