import configparser
import time
from datetime import datetime

from django.test import TestCase
from elasticsearch import Elasticsearch

from flats.models import Advert
from flats.utils import find_ids, get_field_cound

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('settings_server.ini')

ES_SOCKET = config.get('ES', 'ES_SOCKET')


ES_TEST_DATA = {'sku': 12345, 'title': 'Сдается однокомнатная квартира в Соломенском районе'}
FIELD_COUNT_TEST_DATA = {'title': 'testA',
                         'description': 'test',
                         'rooms_count': 0,
                         'price_usd': 0,
                         'price_uah': 0,
                         'url': 'test',
                         'district': 'test',
                         'sku': 123,
                         'image_url': 'test',
                         'published_at': datetime.strptime('08.05.2019'.strip(), '%d.%m.%Y')}


class TestUtils(TestCase):

    @classmethod
    def setUpTestData(cls):
        es = Elasticsearch("{}".format(ES_SOCKET), use_ssl=False)
        es.index(index='test_elasticsearch',
                 doc_type='test_elasticsearch',
                 body=ES_TEST_DATA)
        Advert.objects.create(**FIELD_COUNT_TEST_DATA)

    def test_find_ids(self):
        time.sleep(5)
        test_result = find_ids(search_template='однокомнатная', index='test_elasticsearch')
        print(test_result)
        self.assertEqual(first=test_result[0], second=12345)

    def test_get_field_cound(self):
        result = get_field_cound('district')
        status = False
        for dist in result:
            if dist.get('district') == 'test':
                status = True
                break
        self.assertTrue(status)

    def tearDown(cls):
        time.sleep(3)
        es = Elasticsearch('{}'.format(ES_SOCKET), use_ssl=False)
        es.indices.delete(index='test_elasticsearch')
        Advert.objects.filter(title='testA').delete()
