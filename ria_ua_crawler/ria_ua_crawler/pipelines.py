# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import configparser
import logging
from datetime import datetime

import psycopg2
from elasticsearch import Elasticsearch
from scrapy import log

logger = logging.getLogger(__name__)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('../settings_server.ini')
PG_DB_NAME = config.get('PG', 'PG_DB_NAME')
PG_USER = config.get('PG', 'PG_USER')
PG_TB_NAME = config.get('PG', 'PG_TB_NAME')
PG_HOST = config.get('PG', 'PG_HOST')
PG_PASS = config.get('PG', 'PG_PASS')
ES_SOCKET = config.get('ES', 'ES_SOCKET')


class RiaUaCrawlerPipelinePostgres(object):
    def __init__(self):
        self.connection = psycopg2.connect(
                                           "dbname={dbname} "
                                           "user={user}".format(
                                                                dbname=PG_DB_NAME,
                                                                user=PG_USER))
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS 
                                    flats_advert
                                    (title TEXT, 
                                    description TEXT, 
                                    rooms_count INTEGER,
                                    price_usd REAL,
                                    price_uah REAL,
                                    url VARCHAR(200),
                                    district VARCHAR(200),
                                    sku INTEGER PRIMARY KEY,
                                    image_url VARCHAR(200),
                                    published_at DATE);
                            """)

    def process_item(self, item, spider):
        """ This method is called for every item pipeline component.
        Pipeline uses for save data to PostgreSQL.

        :param item: container which collect all scraped data
        :param spider: spider specifications
        :return: container which collect all scraped data
        """
        try:
            self.cursor.execute("SELECT * FROM {table} WHERE sku={sku} ;".format(table=PG_TB_NAME,
                                                                                 sku=item.get('sku')))
        except:
            self.cursor.execute("ROLLBACK")
        result = self.cursor.fetchone()
        if result:
            log.msg("Item already in PostgreSQL")
            self.cursor.execute("""
                            UPDATE {table}
                            SET 
                            price_usd = {price_usd}, 
                            price_uah = {price_uah}
                            WHERE sku={sku}
            """.format(table=PG_TB_NAME,
                       price_usd=float(item.get('price_USD')),
                       price_uah=float(item.get('price_UAH').replace(' ', '')),
                       sku=item.get('sku')))
            log.msg("Item update in PostgreSQL")
        else:
            self.cursor.execute(
                """
                INSERT INTO
                        flats_advert
                        (title, description, rooms_count, price_usd, price_uah, 
                        url, district, sku, image_url, published_at)
                VALUES
                        ('{title}', '{description}', '{rooms_count}', '{price_usd}', '{price_uah}', 
                        '{url}', '{district}','{sku}','{image_url}', '{published_at}');
                    
                """.format(title=item.get('title', 'Название не задано.'),
                           description=item.get('description', 'Описание не задано.'),
                           rooms_count=item.get('rooms_count', 'Количество комнат не задано.'),
                           price_usd=float(item.get('price_USD')),
                           price_uah=float(item.get('price_UAH').replace(' ', '')),
                           url=item.get('url'),
                           district=item.get('district', 'Район не задано.'),
                           sku=item.get('sku', 'Код не задано.'),
                           image_url=item.get('image_url', 'Изображение не задано.'),
                           published_at=datetime.strptime(item.get('published_at').strip(), '%d.%m.%Y')))
            self.connection.commit()

            log.msg("Item stored in PostgreSQL")
        return item


class RiaUaCrawlerPipelineElasticSearch(object):
    def __init__(self):
        self.connection = Elasticsearch("{}".format(ES_SOCKET), use_ssl=False)

    def exist_data(self, item, spider):
        """ Checking for exist scraped data in Elasticsearch

        :param item: container which collect all scraped data
        :param spider: spider specifications
        :return: bool, False if scraped data exist in Elasticsearch else True
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
                log.msg("Item already in Elasticsearch")
        else:
            return True

    def process_item(self, item, spider):
        """ This method is called for every item pipeline component.
        Pipeline uses for save data to Elasticsearch.

        :param item: container which collect all scraped data
        :param spider: spider specifications
        :return: container which collect all scraped data
        """
        search_result = self.exist_data(item, spider)
        if search_result:
            data = {'title': item.get('title', 'Название не задано.'),
                    'description': item.get('description', 'Описание не задано.'),
                    'rooms_count': item.get('rooms_count', 'Количество комнат не задано.'),
                    'price_USD': float(item.get('price_USD')),
                    'price_UAH': float(item.get('price_UAH').replace(' ', '')),
                    'url': item.get('url'),
                    'district': item.get('district', 'Район не задано.'),
                    'sku':  item.get('sku', 'Код не задано.'),
                    'image_url': item.get('image_url', 'Изображение не задано.'),
                    'published_at': datetime.strptime(item.get('published_at').strip(), '%d.%m.%Y')}
            self.connection.index(index='{}_index'.format(spider.name),
                                  doc_type='{}_doctype'.format(spider.name),
                                  body=data)
            log.msg("Item stored in ES")
        return item


