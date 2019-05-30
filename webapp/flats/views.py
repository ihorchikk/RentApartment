from django.shortcuts import render
from .models import Advert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, QuerySet


# Create your views here.


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


def flats_list(request):
    flats = Advert.objects.all()
    district = Advert.objects.values('district').annotate(dcount=Count('district'))
    contacts = paginator_handler(request, flats)
    return render(request, 'flats/index.html', context={'contacts': contacts,
                                                        'district': district})


def sort_by_price_asc(request):
    flats = Advert.objects.all().order_by("-price_UAH")
    contacts = paginator_handler(request, flats)
    return render(request, 'flats/index.html', context={'contacts': contacts})


def sort_by_price_desc(request):
    flats = Advert.objects.all().order_by("price_UAH")
    contacts = paginator_handler(request, flats)
    return render(request, 'flats/index.html', context={'contacts': contacts})
