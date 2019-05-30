# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import scrapy
from scrapy.loader import ItemLoader
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.response import open_in_browser

from ria_ua_crawler.items import RiaLoader, RiaUaCrawlerItem


class DomRiaComSpider(scrapy.Spider):
    name = 'dom.ria.com'
    allowed_domains = ['dom.ria.com']
    start_urls = ['https://dom.ria.com/arenda-kvartir/kiev/']

    def parse(self, response):
        pages_count = (response.xpath('//span[contains(text(), "...")]/'
                                     'following-sibling::span[@class="page-item mhide"]/a/text()').extract())
        pages_count = [1]
        for page in range(1, int(*pages_count)+1):
            yield scrapy.Request(url=f'{response.url}?page={page}',
                                 callback=self.parse_category)

    def parse_category_item(self, response):
        jsonresponse = response.xpath('//script[@type="application/ld+json"]/text()').extract()
        if jsonresponse:
            json_data = json.loads(*jsonresponse)[0]
            for data in json_data.get('@graph'):
                l = RiaLoader(RiaUaCrawlerItem(), response=response)
                l.add_value('title', data.get('name'))
                l.add_value('description', data.get('description'))
                l.add_value('price_USD', data['offers']['price'])

                sku = data['offers']['sku']
                l.add_xpath('price_UAH', f'//section[@data-realtyid="{sku}"]//b[@title="Цена"]/text()')
                l.add_xpath('district', f'//section[@data-realtyid="{sku}"]//h3[contains(@class,"size18")]'
                                        f'/a/text()[1]')
                l.add_xpath('rooms_count', f'//section[@data-realtyid="{sku}"]//li[@title="Комнат"]/text()', re='\d+')
                item_url = l.get_xpath(f'//section[@data-realtyid="{sku}"]//a[@class="blue"]/@href')
                l.add_value('url', urljoin(response.url, *item_url))
                yield l.load_item()

        else:
            raise ValueError('jsonresponse is empty')

    def parse_category(self, response):
        urls = response.xpath('//a[@class="all-clickable unlink"]/@href').extract()
        for url in urls:
            yield scrapy.Request(url=urljoin(response.url, url),
                                 callback=self.parse_item)

    def parse_item(self, response):
        if response.xpath('//dl[@class="head__page-404"]').extract():
            return HttpError('404 Not found')
        l = RiaLoader(RiaUaCrawlerItem(), response=response)
        jsonresponse = response.xpath('//script[@type="application/ld+json" and contains(text(), "Product")]/text()').extract()
        if jsonresponse:
            json_data = json.loads(*jsonresponse)[0]
            l.add_value('title', json_data.get('name'))
            l.add_value('image_url', json_data.get('image'))
            l.add_value('description', json_data.get('description'))
            l.add_value('price_USD', json_data.get('offers').get('price'))
            l.add_value('sku', json_data.get('sku'))

        l.add_xpath('title', '//h1/text()')
        l.add_xpath('price_USD', '//span[@class="grey size13"]/text()')
        l.add_xpath('price_UAH', '//span[@class="price"]/text()')
        l.add_xpath('district', '//h1', re='р‑н?.\s+?(.+?),')
        l.add_xpath('rooms_count', '//*[@title="комнат"]/text()', re='(\d+)')
        l.add_value('url', response.url)
        l.add_xpath('published_at', '//*[contains(text(),"Опубликовано")]/text()[2]')
        yield l.load_item()

