from django.urls import path

from flats.views import sort_by_price_asc, sort_by_price_desc, search_page
from .views import flats_list

urlpatterns = [
    path('', flats_list, name='flats_list'),
    path('sort_by_price_asc',  sort_by_price_asc, name='sort_by_price_asc'),
    path('sort_by_price_desc', sort_by_price_desc, name='sort_by_price_desc'),
    path('search', search_page, name='search_page'),
]
