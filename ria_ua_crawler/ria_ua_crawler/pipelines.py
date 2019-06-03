# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import configparser
from datetime import datetime

import psycopg2
from elasticsearch import Elasticsearch
from scrapy import log

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('../settings_server.ini')
PG_DB_NAME = config.get('PG', 'PG_DB_NAME')
PG_USER = config.get('PG','PG_USER')
PG_TB_NAME = config.get('PG','PG_TB_NAME')
ES_SOCKET = config.get('ES','ES_SOCKET')


class RiaUaCrawlerPipelinePostgres(object):
    def __init__(self):
        self.connection = psycopg2.connect("dbname={dbname} user={user}".format(dbname=PG_DB_NAME,
                                                                                user=PG_USER))
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS 
                                    flats_advert
                                    (title VARCHAR(200), 
                                    description VARCHAR(1000), 
                                    rooms_count INTEGER,
                                    price_USD REAL,
                                    price_UAH REAL,
                                    url VARCHAR(200),
                                    district VARCHAR(200),
                                    sku INTEGER PRIMARY KEY,
                                    image_url VARCHAR(200),
                                    published_at DATE);
                            """)

    def process_item(self, item, spider):
        """

        :param item:
        :param spider:
        :return:
        """
        self.cursor.execute("SELECT * FROM {} WHERE sku={} ;".format(PG_TB_NAME, item.get('sku')))
        result = self.cursor.fetchone()
        if result:
            # TODO change to update data in table
            log.msg("Item already in PostgreSQL")
        else:
            published_at = item.get('published_at').strip() if item.get('published_at') else str(datetime.now())
            self.cursor.execute(
                """
                INSERT INTO
                        flats_advert
                        (title, description, rooms_count, price_usd, price_uah, 
                        url, district, sku, image_url, published_at)
                VALUES
                        ('{title}', '{description}', '{rooms_count}', '{price_usd}', '{price_uah}', 
                        '{url}', '{district}','{sku}','{image_url}', '{published_at}');
                    
                """.format(title=item.get('title', 'Not found title'),
                           description=item.get('description', 'Not found description'),
                           rooms_count=item.get('rooms_count', 'Not found rooms_count'),
                           price_usd=float(item.get('price_USD')),
                           price_uah=float(item.get('price_UAH').replace(' ', '')),
                           url=item.get('url', 'Not found url'),
                           district=item.get('district', 'Not found district'),
                           sku=item.get('sku', 'Not found sku'),
                           image_url=item.get('image_url', 'Not found image_url'),
                           published_at=datetime.strptime(published_at, '%d.%m.%Y')))
            self.connection.commit()

            log.msg("Item stored in PostgreSQL")
        return item


class RiaUaCrawlerPipelineElasticSearch(object):
    def __init__(self):
        self.connection = Elasticsearch("{}".format(ES_SOCKET), use_ssl=False)

    def exist_data(self, item, spider):
        """

        :param item:
        :param spider:
        :return:
        """
        if self.connection.indices.exists(index='{}_index'.format(spider.name)):
            search_query = {"stored_fields": ["sku"],
                            "query":
                                {"term":
                                    {"sku": item['sku']}
                                 }
                            }
            search_result = self.connection.search(index='{}_index'.format(spider.name), body=search_query)
            if search_result['hits']['total'] == 0:
                return True
            else:
                # TODO change to update data in index
                log.msg("Item already in Elasticsearch")
        else:
            return True

    def process_item(self, item, spider):
        """

        :param item:
        :param spider:
        :return:
        """
        search_result = self.exist_data(item, spider)
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
            self.connection.index(index='{}_index'.format(spider.name),
                                  doc_type='{}_doctype'.format(spider.name),
                                  body=data)
        else:
            log.msg("Item stored in ES")
        return item


