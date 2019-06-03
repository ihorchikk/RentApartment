# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

import psycopg2
from elasticsearch import Elasticsearch
from scrapy import log
import redis


class RiaUaCrawlerPipelinePostgres(object):
    def __init__(self):
        self.connection = psycopg2.connect("dbname=appartments user=ihorchikk")
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS flats_advert '
                            '(title VARCHAR(200), '
                            'description VARCHAR(1000),'
                            'rooms_count INTEGER,'
                            'price_USD REAL,'
                            'price_UAH REAL,'
                            'url VARCHAR(200),'
                            'district VARCHAR(200),'
                            'sku INTEGER PRIMARY KEY,'
                            'image_url VARCHAR(200),'
                            'published_at DATE);')

    def process_item(self, item, spider):
        self.cursor.execute(f"SELECT * FROM flats_advert WHERE sku={item.get('sku')} ;")
        result = self.cursor.fetchone()
        if result:
            # TODO need to update data
            log.msg("Item already in database")
        else:
            self.cursor.execute(
                "INSERT INTO "
                "flats_advert (title, description, rooms_count, price_usd, price_uah, url, district, sku, image_url, published_at) "
                f"VALUES ('{item.get('title', 'Not found title')}', "
                f"'{item.get('description', 'Not found description')}', "
                f"'{item.get('rooms_count', 'Not found rooms_count')}', "
                f"'{float(item.get('price_USD'))}', "
                f"'{float(item.get('price_UAH').replace(' ', ''))}',"
                f"'{item.get('url', 'Not found url')}',"
                f"'{item.get('district', 'Not found district')}',"
                f"'{item.get('sku', 'Not found sku')}',"
                f"'{item.get('image_url', 'Not found image_url')}',"
                f"'{datetime.strptime(item.get('published_at').strip(), '%d.%m.%Y')}');"
                 )
            self.connection.commit()

            log.msg("Item stored in SQLite")
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

    def exist_data(self, item):
        search_query = {"stored_fields": ["sku"],
                        "query":
                            {"term":
                                {"sku": item['sku']}
                             }
                        }
        search_result = self.connection.search(index='dom.ria.com_index', body=search_query)
        if search_result['hits']['total'] == 0:
            return True

    def process_item(self, item, spider):

        search_result = self.exist_data(item)
        if search_result:
            data = {'title': item.get('title', 'Not found title'),
                    'description': item.get('description', 'Not found description'),
                    'rooms_count': item.get('rooms_count', 'Not found rooms_count'),
                    'price_USD': float(item.get('price_USD')),
                    'price_UAH': float(item.get('price_UAH').replace(' ', '')),
                    'url': item.get('url', 'Not found url'),
                    'district': item.get('district', 'Not found district'),
                    'sku':  item.get('sku', 'Not found sku'),
                    'image_url': item.get('image_url', 'Not found image_url'),
                    'published_at': datetime.strptime(item.get('published_at').strip(), '%d.%m.%Y')}
            self.connection.index(index=f'{spider.name}_index', doc_type=f'{spider.name}_doctype', body=data)
        else:
            log.msg("Item stored in ES")
        return item


