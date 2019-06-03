# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


class RiaUaCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = Field(required=True)
    description = Field(required=True)
    rooms_count = Field(required=True)
    price_USD = Field(type='float', required=True)
    price_UAH = Field(type='int', required=True)
    url = Field(required=True)
    district = Field(required=True)
    sku = Field(required=True, )
    image_url = Field(required=True)
    published_at = Field()


class RiaLoader(ItemLoader):

    default_output_processor = TakeFirst()
    title_in = MapCompose(str.strip)
    title_out = Join()
    district_in = MapCompose(str.strip)