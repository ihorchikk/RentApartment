from django.shortcuts import render
from elasticsearch import Elasticsearch

from flats.forms import FilterAndSearch
from .models import Advert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count


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


def flats_list(request):
    filter_paged = filter_fields(request)
    flats = Advert.objects.all().filter(**filter_paged) if filter_paged else Advert.objects.all()
    district, rooms_count = get_district_and_rooms()
    contacts = paginator_handler(request, flats)
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count})


def sort_by_price_asc(request):
    filter_paged = filter_fields(request)
    flats = Advert.objects.all().order_by("-price_UAH").filter(**filter_paged) \
        if filter_paged else Advert.objects.all().order_by("-price_UAH")
    contacts = paginator_handler(request, flats)
    district, rooms_count = get_district_and_rooms()
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count})


def sort_by_price_desc(request):
    filter_paged = filter_fields(request)
    flats = Advert.objects.all().order_by("price_UAH").filter(**filter_paged) \
        if filter_paged else Advert.objects.all().order_by("price_UAH")
    contacts = paginator_handler(request, flats)
    district, rooms_count = get_district_and_rooms()
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count})


def filter_fields(request):
    if request.method == 'POST':
        form = FilterAndSearch(request.POST)
        if form.is_valid():
            fields = ['district', 'rooms_count', 'price_from', 'price_to']
            result_filters = dict()
            for field in fields:
                data = form.cleaned_data[field]
                if data:
                    result_filters[field] = data
            return result_filters


def get_district_and_rooms():
    district = Advert.objects.values('district').annotate(dcount=Count('district'))
    rooms_count = Advert.objects.values('rooms_count').annotate(dcount=Count('rooms_count'))
    return district, rooms_count


def search_page(request):
    search_data = request.GET.get('search_data', '')
    if search_data:
        ids = find_ids(search_data)
        if ids:
            flats = Advert.objects.filter(sku__in=ids)
            district = Advert.objects.values('district').annotate(dcount=Count('district'))
            rooms_count = Advert.objects.values('rooms_count').annotate(dcount=Count('rooms_count'))
            contacts = paginator_handler(request, flats)
            return render(request, 'flats/index.html', context={'contacts': contacts,
                                                                'district': district,
                                                                'rooms_count': rooms_count})
        else:
            return render(request, 'flats/not_found.html')
    else:
        return render(request, 'flats/search_page.html')

