from django.urls import path

from flats.views import sort_view
from .views import flats_views

urlpatterns = [
    path('', flats_views, name='flats_list'),
    path('sort_by_price_asc',  sort_view, name='sort_by_price_asc'),
    path('sort_by_price_desc', sort_view, name='sort_by_price_desc'),
    path('sort_by_date_asc', sort_view, name='sort_by_date_asc'),
    path('sort_by_date_desc', sort_view, name='sort_by_date_desc')
]
