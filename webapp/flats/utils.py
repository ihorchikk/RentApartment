import configparser

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from elasticsearch import Elasticsearch

from flats.forms import Filter
from flats.models import Advert

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('settings_server.ini')

ES_SOCKET = config.get('ES', 'ES_SOCKET')
ES_INDEX = config.get('ES', 'ES_INDEX')
ITEMS_PER_PAGE = config.get('Django', 'ITEMS_PER_PAGE')


def paginator_handler(request, flats):
    '''

    :param request:
    :param flats:
    :return:
    '''
    paginator = Paginator(flats, ITEMS_PER_PAGE)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    return contacts


def find_ids(search_template):
    '''

    :param search_template:
    :return:
    '''
    search_query = {"_source": ["sku"],
                    "query": {
                        "multi_match": {
                            "query": "{}".format(search_template),
                            "fields": ["title", "description"]
                        }
                    }
                    }
    es = Elasticsearch("{}".format(ES_SOCKET), use_ssl=False)
    search_result = es.search(index=''.format(ES_INDEX), body=search_query)
    hits = search_result['hits']['hits']
    return [post['_source']['sku'] for post in hits]


def filter_fields(request):
    '''

    :param request:
    :return:
    '''
    if request.method == 'POST':
        form = Filter(request.POST)
        if form.is_valid():
            fields = ['district', 'rooms_count', 'price_from', 'price_to']
            result_filters = dict()
            for field in fields:
                data = form.cleaned_data[field]
                if data:
                    field = 'price_uah__gte' if field == 'price_from' else field
                    field = 'price_uah__lte' if field == 'price_to' else field
                    result_filters[field] = data
            return {'filters': result_filters, 'search': form.cleaned_data.get('search_data')}
    return {'filters': {}, 'search': {}}


def get_district_and_rooms():
    '''

    :return:
    '''
    district = Advert.objects.values('district').annotate(dcount=Count('district')).order_by('district')
    rooms_count = Advert.objects.values('rooms_count').annotate(dcount=Count('rooms_count')).order_by('rooms_count')
    return district, rooms_count
