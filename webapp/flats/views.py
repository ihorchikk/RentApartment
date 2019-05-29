from django.shortcuts import render
from .models import Advert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def flats_list(request):
    flats = Advert.objects.all()
    paginator = Paginator(flats, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'flats/index.html', context={'contacts': contacts})
