# Generated by Django 2.2.10 on 2020-11-15 04:12

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20190901_0820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 15, 4, 12, 25, 193411, tzinfo=utc), verbose_name='date joined'),
        ),
    ]
