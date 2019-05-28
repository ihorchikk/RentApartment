# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from elasticsearch import Elasticsearch
from scrapy import log
import sqlite3
import redis
import elasticsearch


class RiaUaCrawlerPipelineSQLite3(object):
    def __init__(self):
        # Possible we should be doing this in spider_open instead, but okay
        self.connection = sqlite3.connect('../scrapedata.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS ria_com '
                            '(sku INTEGER PRIMARY KEY, '
                            'title VARCHAR(80), '
                            'description VARCHAR(80),'
                            'price_USD REAL,'
                            'price_UAH REAL,'
                            'district VARCHAR(80),'
                            'rooms_count INTEGER,'
                            'url VARCHAR(80))')

    # Take the item and put it in database - do not allow duplicates
    def process_item(self, item, spider):
        self.cursor.execute("select * from ria_com where url=?", (item.get('url'),))
        result = self.cursor.fetchone()
        if result:
            # TODO need to update data
            log.msg("Item already in database: %s" % item, level=log.DEBUG)
        else:
            self.cursor.execute(
                "insert into ria_com (sku, title, description, price_USD, price_UAH, district, rooms_count, url) "
                "values (?, ?, ?, ?, ?, ?, ?, ?)", (item.get('sku', 'Not found sku'),
                                                    item.get('title', 'Not found title'),
                                                    item.get('description', 'Not found description'),
                                                    item.get('price_USD', 'Not found price_USD'),
                                                    item.get('price_UAH', 'Not found price_UAH'),
                                                    item.get('district', 'Not found district'),
                                                    item.get('rooms_count', 'Not found rooms_count'),
                                                    item.get('url', 'Not found url')
                                                    ))

            self.connection.commit()

            log.msg("Item stored : " % item, level=log.DEBUG)
        return item


class RiaUaCrawlerPipelineRedis(object):
    def __init__(self):
        self.connection = redis.StrictRedis(
            host='127.0.0.1',
            port='6379',
            db=1
        )

    def process_item(self, item, spider):
        if self.connection.exists(item.get('sku')):
            self.connection.delete(item.get('sku'))
            self.connection.hmset(name=item.get('sku'), mapping=item)
        else:
            self.connection.hmset(name=item.get('sku'), mapping=item)
        return item


class RiaUaCrawlerPipelineElasticSearch(object):
    def __init__(self):
        self.connection = Elasticsearch("127.0.0.1:9200", use_ssl=False)

    def process_item(self, item, spider):
        print(self.connection.index(index='test', doc_type='test'))
        # if self.connection.exists(item.get('sku')):
        #     self.connection.delete(item.get('sku'))
        #     self.connection.hmset(name=item.get('sku'), mapping=item)
        # else:
        #     self.connection.hmset(name=item.get('sku'), mapping=item)
        # return item