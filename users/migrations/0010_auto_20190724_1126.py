# Generated by Django 2.2.3 on 2019-07-24 11:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20190720_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2019, 7, 24, 11, 26, 24, 415724, tzinfo=utc), verbose_name='date joined'),
        ),
    ]
