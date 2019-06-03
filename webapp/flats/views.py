from collections import namedtuple

from django.shortcuts import render
from elasticsearch import Elasticsearch

from flats.forms import Filter
from .models import Advert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from ast import literal_eval


def flats_views(request):
    filter_paged = filter_fields(request)
    all_data = Advert.objects.all()
    filters = filter_paged.get('filters')
    search = filter_paged.get('search')
    if search:
        ids = find_ids(search)
        if filters:
            flats = all_data.filter(sku__in=ids).filter(**filters)
        else:
            flats = all_data.filter(sku__in=ids)
    else:
        if filters:
            flats = all_data.filter(**filters)
        else:
            flats = all_data
    district, rooms_count = get_district_and_rooms()
    contacts = paginator_handler(request, flats)
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count,
                                                        'filtered_infromation': filter_paged})


def paginator_handler(request, flats):
    paginator = Paginator(flats, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    return contacts


def find_ids(search_template):
    search_query = {"_source": ["sku"],
                    "query": {
                        "multi_match": {
                            "query": f"{search_template}",
                            "fields": ["title", "description"]
                        }
                    }
                    }
    es = Elasticsearch("127.0.0.1:9200", use_ssl=False)
    search_result = es.search(index='dom.ria.com_index', body=search_query)
    hits = search_result['hits']['hits']
    return [post['_source']['sku'] for post in hits]


def filter_fields(request):
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
    else:
        return {'filters': {}, 'search': {}}


def get_district_and_rooms():
    district = Advert.objects.values('district').annotate(dcount=Count('district'))
    rooms_count = Advert.objects.values('rooms_count').annotate(dcount=Count('rooms_count'))
    return district, rooms_count


def sort_view(request):
    if 'sort_by_price_asc' in request.path:
        order_query = '-price_uah'
    elif 'sort_by_price_desc' in request.path:
        order_query = 'price_uah'
    elif 'sort_by_date_asc' in request.path:
        order_query = '-published_at'
    elif 'sort_by_date_desc' in request.path:
        order_query = 'published_at'
    else:
        raise ValueError('Cannot find sort phrase in request.path')
    filter_data = literal_eval(request.GET.get('filter_data', '{"filter_data": {}}'))
    print(filter_data)
    all_data = Advert.objects.all()
    filters = filter_data.get('filters')
    search = filter_data.get('search')
    if search:
        ids = find_ids(search)
        if filters:
            flats = all_data.order_by(f"{order_query}").filter(sku__in=ids).filter(**filters)
        else:
            flats = all_data.order_by(f"{order_query}").filter(sku__in=ids)
    else:
        if filters:
            flats = all_data.order_by(f"{order_query}").filter(**filters)
        else:
            flats = all_data.order_by(f"{order_query}")
    contacts = paginator_handler(request, flats)
    district, rooms_count = get_district_and_rooms()
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count,
                                                        'filtered_infromation': filter_data})

