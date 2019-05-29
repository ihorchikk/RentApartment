# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader, Identity
from scrapy.loader.processors import TakeFirst, MapCompose, Join


class RiaUaCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field(required=True)
    description = scrapy.Field(required=True)
    rooms_count = scrapy.Field(required=True)
    price_USD = scrapy.Field(required=True, )
    price_UAH = scrapy.Field(required=True)
    url = scrapy.Field(required=True)
    district = scrapy.Field(required=True)
    sku = scrapy.Field(required=True)


class RiaLoader(ItemLoader):

    default_output_processor = TakeFirst()
    title_in = MapCompose(str.strip)
    title_out = Join()
    district_in = MapCompose(str.strip)
