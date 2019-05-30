from django.db import models

# Create your models here.
from django.forms import ModelForm, DateField
from django.utils import timezone



class Advert(models.Model):
    # id = models.IntegerField(primary_key=True, db_index=True)
    title = models.CharField(max_length=80, db_index=True)
    description = models.SlugField(max_length=200, db_index=True)
    rooms_count = models.IntegerField(db_index=True)
    price_USD = models.FloatField(db_index=True)
    price_UAH = models.FloatField(db_index=True)
    url = models.CharField(max_length=80, db_index=True)
    district = models.CharField(max_length=80, db_index=True)
    sku = models.IntegerField(primary_key=True, db_index=True)
    image_url = models.CharField(max_length=80, db_index=True, default='Not found image')
    # published_at = models.DateField(input_formats=())

    def __str__(self):
        return f'{self.title}'


