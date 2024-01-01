# This file is added because I found the comos problem after I have scrapped a lot of news.

import sqlite3

dbconn = sqlite3.connect('newsInfo.db')

items = dbconn.execute('SELECT docid FROM news WHERE docid LIKE "comos:%"').fetchall()

for item in items:
    cursor = dbconn.execute(f'UPDATE OR IGNORE news SET docid = "{item[0][6:]}" WHERE docid = "{item[0]}"')

    # The doc exists in the database
    if cursor.rowcount == 0:
        dbconn.execute(f'DELETE FROM news WHERE docid = "{item[0]}"')
    
dbconn.commit()