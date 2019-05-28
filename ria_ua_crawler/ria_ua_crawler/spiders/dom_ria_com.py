# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import scrapy
from scrapy.loader import ItemLoader

from ria_ua_crawler.items import RiaLoader, RiaUaCrawlerItem


class DomRiaComSpider(scrapy.Spider):
    name = 'dom.ria.com'
    allowed_domains = ['dom.ria.com']
    start_urls = ['https://dom.ria.com/arenda-kvartir/kiev/']

    def parse(self, response):
        pages_count = (response.xpath('//span[contains(text(), "...")]/'
                                      'following-sibling::span[@class="page-item mhide"]/a/text()').extract())
        for page in range(1, int(*pages_count)+1):
            yield scrapy.Request(url=f'{response.url}?page={page}',
                                 callback=self.parse_category)

    def parse_category(self, response):
        jsonresponse = response.xpath('//script[@type="application/ld+json"]/text()').extract()
        if jsonresponse:
            json_data = json.loads(*jsonresponse)[0]
            for data in json_data.get('@graph'):
                l = RiaLoader(RiaUaCrawlerItem(), response=response)
                l.add_value('title', data.get('name'))
                l.add_value('description', data.get('description'))
                l.add_value('price_USD', data['offers']['price'])
                l.add_value('sku', data['offers']['sku'])

                sku = data['offers']['sku']
                l.add_xpath('price_UAH', f'//section[@data-realtyid="{sku}"]//b[@title="Цена"]/text()', re='\d+\s\d+')
                l.add_xpath('district', f'//section[@data-realtyid="{sku}"]//h3[contains(@class,"size18")]'
                                        f'/a/text()[1]')
                l.add_xpath('rooms_count', f'//section[@data-realtyid="{sku}"]//li[@title="Комнат"]/text()', re='\d+')
                item_url = l.get_xpath(f'//section[@data-realtyid="{sku}"]//a[@class="blue"]/@href')
                l.add_value('url', urljoin(response.url, *item_url))
                yield l.load_item()

        else:
            raise ValueError('jsonresponse is empty')

