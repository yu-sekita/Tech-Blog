# Generated by Django 2.2.4 on 2019-09-01 08:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20190816_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 1, 8, 20, 22, 84676, tzinfo=utc), verbose_name='date joined'),
        ),
    ]
