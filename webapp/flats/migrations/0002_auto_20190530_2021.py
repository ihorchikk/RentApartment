# Generated by Django 2.2.1 on 2019-05-30 20:21

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('flats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advert',
            name='published_at',
            field=models.DateField(default=datetime.datetime(2019, 5, 30, 20, 21, 39, 41100, tzinfo=utc)),
        ),
    ]
