# Generated by Django 2.2.3 on 2019-07-18 14:27

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0005_auto_20190718_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 7, 18, 14, 27, 7, 647178, tzinfo=utc), verbose_name='作成日'),
        ),
    ]