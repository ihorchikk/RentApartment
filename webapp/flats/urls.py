from django.urls import path
from .views import flats_list

urlpatterns = [
    path('', flats_list),
]
