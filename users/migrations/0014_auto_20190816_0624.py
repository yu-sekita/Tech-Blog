# Generated by Django 2.2.4 on 2019-08-16 06:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20190813_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 16, 6, 24, 8, 947670, tzinfo=utc), verbose_name='date joined'),
        ),
    ]