# Generated by Django 2.2.3 on 2019-07-19 12:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0008_auto_20190718_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 7, 19, 12, 48, 34, 75207, tzinfo=utc), verbose_name='作成日'),
        ),
    ]
