# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import log
import sqlite3

# This pipeline takes the Item and stuffs it into scrapedata.db
class RiaUaCrawlerPipeline(object):
    def __init__(self):
        # Possible we should be doing this in spider_open instead, but okay
        self.connection = sqlite3.connect('../scrapedata.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ria_com '
                            '(id INTEGER PRIMARY KEY, '
                            'title VARCHAR(80), '
                            'description VARCHAR(80),'
                            'price_USD REAL,'
                            'price_UAH REAL,'
                            'district VARCHAR(80),'
                            'rooms_count INTEGER,'
                            'url VARCHAR(80))')

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):
        self.cursor.execute("select * from ria_com where url=?", (item['url'],))
        result = self.cursor.fetchone()
        if result:
            print('  '* 1000)
            log.msg("Item already in database: %s" % item, level=log.DEBUG)
        else:
            self.cursor.execute(
                "insert into ria_com (title, description, price_USD, price_UAH, district, rooms_count, url) "
                "values (?, ?, ?, ?, ?, ?, ?)", (item['title'],
                                                 item['description'],
                                                 item['price_USD'],
                                                 item['price_UAH'],
                                                 item['district'],
                                                 item['rooms_count'],
                                                 item['url']
                                                 ))

            self.connection.commit()

            log.msg("Item stored : " % item, level=log.DEBUG)
        return item

    def handle_error(self, e):
        log.err(e)
