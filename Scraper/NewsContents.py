import requests
import bs4
from bs4 import BeautifulSoup
import lxml
import re
import sqlite3
import json
from Constants import Constants
import os
import time
import random

dbconn = sqlite3.connect('newsInfo.db')

dbconn.execute('''\
CREATE TABLE IF NOT EXISTS contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    docid TEXT UNIQUE NOT NULL,
    raw_html TEXT NOT NULL,
    content TEXT NOT NULL,
    image_info TEXT NOT NULL,
    CONSTRAINT fk_docid FOREIGN KEY (docid) REFERENCES news (docid)
)
''')

CrawledImageFolder = 'images/crawled/'
if not os.path.exists(CrawledImageFolder):
    os.mkdir(CrawledImageFolder)

TechSinaURLPattern = re.compile(r'^https?://tech\.sina\.com\.cn/')
FinanceSinaURLPattern = re.compile(r'^https?://finance\.sina\.com\.cn/')
ZhongCeSinaURLPattern = re.compile(r'^https?://zhongce\.sina\.com\.cn/')

RemoveAdditionalLineBreaksPattern = re.compile(r'\n\n+')

def GetTechSinaNewsContent(docid: str, newsUrl: str) -> None:
    assert TechSinaURLPattern.match(newsUrl) is not None

    print(f'Parsing {docid}...')

    resp = requests.get(newsUrl, headers={
        'User-Agent': Constants.GetRandomUserAgent()
    })

    resp.encoding = 'utf-8'
    resp.raise_for_status()

    raw_html = resp.text

    soup = BeautifulSoup(raw_html, 'lxml')

    media_name_span = soup.find(id='media_name')
    if media_name_span is not None:
        media_name_a = media_name_span.find(attrs={
            'data-sudaclick': 'media_name'
        })

        if media_name_a is not None:
            media_name = media_name_a.text.strip()

            # Update media name if empty
            if dbconn.execute(f'SELECT media_name FROM news WHERE docid = "{docid}"').fetchone()[0].strip() == "":
                dbconn.execute(f'UPDATE news SET media_name = "{media_name}" WHERE docid = "{docid}"')
    
    author_span = soup.find(id='author_ename')
    if author_span is not None:
        author_a = author_span.find('a')
        if author_a is not None:
            author = author_a.text.strip()

            # Update author if empty
            if dbconn.execute(f'SELECT author FROM news WHERE docid = "{docid}"').fetchone()[0].strip() == "":
                dbconn.execute(f'UPDATE news SET author = "{author}" WHERE docid = "{docid}"')
    
    # No tag found for this category

    images = {}

    content_div = soup.find(id='artibody')
    for image_div in content_div.find_all('div', class_='img_wrapper'):
        # Used as type specification
        # image_div = bs4.element.Tag(image_div)

        image = image_div.find('img')
        image_source = image['src']

        # A placeholder to replace the local image there later
        image_placeholder = soup.new_tag('p')
        image_placeholder.string = f"<_IMAGE_{len(images)}_{image['src']}_/>"
        image_div.append(image_placeholder)
        
        local_image_path = CrawledImageFolder + docid + '_' + str(len(images)) + image_source[image_source.rfind('.'):]

        if image_source.startswith('//'):
            image_source = 'http:' + image_source
        elif image_source.startswith('/'):
            image_source = 'http://tech.sina.com.cn' + image_source

        images[len(images)] = [image_source, local_image_path]

        # Some additional news's images are not downloaded to save disk space. They may be downloaded later.
        try:
            with open(local_image_path, 'wb') as f:
                f.write(requests.get(image_source, headers={'User-Agent': Constants.GetRandomUserAgent()}).content)
            
            print(f'Downloaded image {image_source} to {local_image_path}')
        except Exception as e:
            print(f'Failed to download image {image_source} :', e)

    content = RemoveAdditionalLineBreaksPattern.sub("\n", content_div.text).strip()

    cursor = dbconn.execute(f'''\
INSERT OR IGNORE INTO contents (docid, raw_html, content, image_info)
VALUES (
    "{docid}",
    "{raw_html.replace('"', '""')}",
    "{content.replace('"', '""')}",
    "{json.dumps(images).replace('"', '""')}"
)
''')
    
    if cursor.rowcount > 0:
        print(f'DB: Inserted {docid}')
    else:
        print(f'DB: Skipped {docid} (Should not happen)')

    dbconn.execute(f'UPDATE news SET content_downloaded = 1 WHERE docid = "{docid}"')

    dbconn.commit()

# GetTechSinaNewsContent('mziknym5761431', 'https://tech.sina.com.cn/csj/2023-08-25/doc-imziknym5761431.shtml')

def GetFinanceSinaNewsContent(docid: str, newsUrl: str) -> None:
    assert FinanceSinaURLPattern.match(newsUrl) is not None

    print(f'Parsing {docid}...')

    resp = requests.get(newsUrl, headers={
        'User-Agent': Constants.GetRandomUserAgent()
    })

    resp.encoding = 'utf-8'
    resp.raise_for_status()

    raw_html = resp.text

    soup = BeautifulSoup(raw_html, 'lxml')

    media_name_span = soup.find(class_='ent-source')
    if media_name_span is not None:
        media_name = media_name_span.text.strip()

        # Update media name if empty
        if dbconn.execute(f'SELECT media_name FROM news WHERE docid = "{docid}"').fetchone()[0].strip() == "":
            dbconn.execute(f'UPDATE news SET media_name = "{media_name}" WHERE docid = "{docid}"')
    
    # No author found for this category

    tags_div = soup.find(attrs={'data-sudaclick': 'content_keywords_p'})
    if tags_div is not None:
        tags = [tag.text.strip() for tag in tags_div.find_all('a')]

        # Update tags if empty
        dbTags = dbconn.execute(f'SELECT tags FROM news WHERE docid = "{docid}"').fetchone()[0]
        if dbTags is None or dbTags.strip() == "":
            dbconn.execute(f'UPDATE news SET tags = "{",".join(tags)}" WHERE docid = "{docid}"')
    
    images = {}

    # The code are almost the same as TechSina...
    content_div = soup.find(id='artibody')
    for image_div in content_div.find_all('div', class_='img_wrapper'):
        # Used as type specification
        # image_div = bs4.element.Tag(image_div)

        image = image_div.find('img')
        image_source = image['src']

        # A placeholder to replace the local image there later
        image_placeholder = soup.new_tag('p')
        image_placeholder.string = f"<_IMAGE_{len(images)}_{image['src']}_/>"
        image_div.append(image_placeholder)
        
        local_image_path = CrawledImageFolder + docid + '_' + str(len(images)) + image_source[image_source.rfind('.'):]

        if image_source.startswith('//'):
            image_source = 'http:' + image_source
        elif image_source.startswith('/'):
            image_source = 'http://tech.sina.com.cn' + image_source

        images[len(images)] = [image_source, local_image_path]

        try:
            with open(local_image_path, 'wb') as f:
                f.write(requests.get(image_source, headers={'User-Agent': Constants.GetRandomUserAgent()}).content)
            
            print(f'Downloaded image {image_source} to {local_image_path}')
        except Exception as e:
            print(f'Failed to download image {image_source} :', e)

    # Remove ads
    ad1 = content_div.find(class_='app-kaihu-qr')
    if ad1 is not None:
        ad1.extract()
    
    ad2 = content_div.find(class_='appendQr_wrap')
    if ad2 is not None:
        ad2.extract()

    content = RemoveAdditionalLineBreaksPattern.sub("\n", content_div.text).strip()

    cursor = dbconn.execute(f'''\
INSERT OR IGNORE INTO contents (docid, raw_html, content, image_info)
VALUES (
    "{docid}",
    "{raw_html.replace('"', '""')}",
    "{content.replace('"', '""')}",
    "{json.dumps(images).replace('"', '""')}"
)
''')
    
    if cursor.rowcount > 0:
        print(f'DB: Inserted {docid}')
    else:
        print(f'DB: Skipped {docid} (Should not happen)')

    dbconn.execute(f'UPDATE news SET content_downloaded = 1 WHERE docid = "{docid}"')

    dbconn.commit()

# GetFinanceSinaNewsContent('mzimcwc5497874', 'https://finance.sina.com.cn/stock/usstock/c/2023-08-25/doc-imzimcwc5497874.shtml')

def GetZhongceSinaNewsContent(docid: str, url: str):
    assert ZhongCeSinaURLPattern.match(url) is not None

    print(f'Parsing {docid}...')

    resp = requests.get(url, headers={
        'User-Agent': Constants.GetRandomUserAgent()
    })

    resp.encoding = 'utf-8'
    resp.raise_for_status()

    raw_html = resp.text

    soup = BeautifulSoup(raw_html, 'lxml')

    # No media name found for this category

    author_span = soup.find(class_='content-head').find(class_='author').find('span')
    if author_span is not None:
        author = author_span.text.strip()

        # Update author if empty
        if dbconn.execute(f'SELECT author FROM news WHERE docid = "{docid}"').fetchone()[0].strip() == "":
            dbconn.execute(f'UPDATE news SET author = "{author}" WHERE docid = "{docid}"')
    
    # No tag found for this category (also)

    images = {}
    content_div = soup.find(id='task_page')
    for image_p in content_div.find_all('p', class_='zc_img'):
        image = image_p.find('img')

        # I really wonder why this happens
        if image is None:
            continue

        image_source = image['src']

        # A placeholder to replace the local image there later
        image_placeholder = soup.new_tag('p')
        image_placeholder.string = f"<_IMAGE_{len(images)}_{image['src']}_/>"
        image_p.append(image_placeholder)
        
        local_image_path = CrawledImageFolder + docid + '_' + str(len(images)) + image_source[image_source.rfind('.'):]

        if image_source.startswith('//'):
            image_source = 'http:' + image_source
        elif image_source.startswith('/'):
            image_source = 'http://tech.sina.com.cn' + image_source

        images[len(images)] = [image_source, local_image_path]

        try:
            with open(local_image_path, 'wb') as f:
                f.write(requests.get(image_source, headers={'User-Agent': Constants.GetRandomUserAgent()}).content)
            
            print(f'Downloaded image {image_source} to {local_image_path}')
        except Exception as e:
            print(f'Failed to download image {image_source} :', e)
    
    content = RemoveAdditionalLineBreaksPattern.sub("\n", content_div.text).strip()
    
    cursor = dbconn.execute(f'''\
INSERT OR IGNORE INTO contents (docid, raw_html, content, image_info)
VALUES (
    "{docid}",
    "{raw_html.replace('"', '""')}",
    "{content.replace('"', '""')}",
    "{json.dumps(images).replace('"', '""')}"
)
''')
    
    if cursor.rowcount > 0:
        print(f'DB: Inserted {docid}')
    else:
        print(f'DB: Skipped {docid} (Should not happen)')

    dbconn.execute(f'UPDATE news SET content_downloaded = 1 WHERE docid = "{docid}"')

    dbconn.commit()

# GetZhongceSinaNewsContent('mzikxpy1253773', 'http://zhongce.sina.com.cn/article/view/172689')

def GetNewsContent(docid: str, url: str) -> None:
    if TechSinaURLPattern.match(url) is not None:
        GetTechSinaNewsContent(docid, url)
    elif FinanceSinaURLPattern.match(url) is not None:
        GetFinanceSinaNewsContent(docid, url)
    elif ZhongCeSinaURLPattern.match(url) is not None:
        GetZhongceSinaNewsContent(docid, url)
    else:
        raise Exception(f'Unknown news category: {url}')

def main():
    cursor = dbconn.execute('SELECT docid, url FROM news WHERE content_downloaded = 0 AND content_download_error IS NULL ORDER BY id DESC')
    items = cursor.fetchall()
    length = len(items)

    for index, item in enumerate(items):
        if item is None:
            print('No more news to parse.')
            break

        print(f'[{index + 1}/{length}] ', end='')

        try:
            GetNewsContent(item[0], item[1])
        except Exception as e:
            print(f'Failed to parse {item[0]} :', e)

            # Mark as error, only uncomment this when you are sure that the error is caused by the website itself.
            # (i.e. Not because the network conn problem when downloading the image or sth)
            dbconn.execute(f'UPDATE news SET content_download_error = 1 WHERE docid = "{item[0]}"')
            dbconn.commit()
        
        # time.sleep(random.randrange(1, 2) / 2)

if __name__ == '__main__':
    main()

dbconn.close()