import configparser
from ast import literal_eval

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from elasticsearch import Elasticsearch

from flats.forms import Filter, FilteredData
from flats.models import Advert

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read('settings_server.ini')

ES_SOCKET = config.get('ES', 'ES_SOCKET')
ES_INDEX = config.get('ES', 'ES_INDEX')
ITEMS_PER_PAGE = config.get('Django', 'ITEMS_PER_PAGE')


def paginator_handler(request, flats):
    """Get adverts per page

    :param request: HTTP request
    :param flats: adverts data
    :return: adverts per page
    """
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
    """ Finding advert by some phrase

    :param search_template: search phrase
    :return: sku of adverts
    """
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
    """ Collect information transmitted by the client and transferring them to views.

    :param request: HTTP request
    :return: dict, collected filters data
    """
    if request.method == 'POST':
        filter_data = Filter(request.POST)
        service_data = FilteredData(request.POST)
        if service_data.is_valid():
            service_data = literal_eval(service_data.cleaned_data['filter_data'])

            fields = ['district', 'rooms_count', 'price_uah__gte', 'price_uah__lte']
            result_filters = dict()
            for field in fields:
                data = service_data.get('filters').get(field)
                if data:
                    result_filters[field] = data
            return {'filters': result_filters, 'search': service_data.get('search')}
        if filter_data.is_valid():
            fields = ['district', 'rooms_count', 'price_from', 'price_to']
            result_filters = dict()
            for field in fields:
                data = filter_data.cleaned_data[field]
                if data:
                    field = 'price_uah__gte' if field == 'price_from' else field
                    field = 'price_uah__lte' if field == 'price_to' else field
                    result_filters[field] = data
            return {'filters': result_filters, 'search': filter_data.cleaned_data.get('search_data')}
    else:
        return {'filters': {}, 'search': {}}


def get_district_and_rooms(field):
    """ Create request to DB for collect information about district and rooms_count

    :param field: searching field
    :return: DB response
    """
    result = Advert.objects.values(field).annotate(dcount=Count(field)).order_by(field)
    return result
