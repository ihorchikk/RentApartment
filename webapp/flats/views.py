from django.http import Http404
from django.shortcuts import render

from flats.utils import (filter_fields, find_ids, get_field_cound,
                         paginator_handler)
from .models import Advert


def flats_views(request):
    """ View of main page

    :param request: HTTP request
    :return: HTTP response
    """

    filter_paged = filter_fields(request)
    all_data = Advert.objects.all()
    filters = filter_paged.get('filters')
    search = filter_paged.get('search')
    if search:
        ids = find_ids(search)
        flats = all_data.filter(sku__in=ids).filter(**filters) if filters else all_data.filter(sku__in=ids)
    else:
        flats = all_data.filter(**filters) if filters else all_data
    district, rooms_count = get_field_cound('district'), get_field_cound('rooms_count')
    contacts = paginator_handler(request, flats)
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count,
                                                        'filtered_infromation': filter_paged})


def sort_view(request):
    """ View of sort page

    :param request: HTTP request
    :return: HTTP response
    """
    if 'sort_by_price_asc' in request.path:
        order_query = '-price_uah'
    elif 'sort_by_price_desc' in request.path:
        order_query = 'price_uah'
    elif 'sort_by_date_asc' in request.path:
        order_query = '-published_at'
    elif 'sort_by_date_desc' in request.path:
        order_query = 'published_at'
    else:
        raise Http404("Page not found")

    filter_data = filter_fields(request)
    all_data = Advert.objects.all().order_by("{}".format(order_query))
    filters = filter_data.get('filters')
    search = filter_data.get('search')

    if search:
        ids = find_ids(search)
        flats = all_data.filter(sku__in=ids).filter(**filters) if filters else all_data.filter(sku__in=ids)
    else:
        flats = all_data.filter(**filters) if filters else all_data

    contacts = paginator_handler(request, flats)
    district, rooms_count = get_field_cound('district'), get_field_cound('rooms_count')
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district,
                                                        'rooms_count': rooms_count,
                                                        'filtered_infromation': filter_data})
