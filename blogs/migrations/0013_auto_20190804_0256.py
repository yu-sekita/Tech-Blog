# Generated by Django 2.2.3 on 2019-08-04 02:56

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0012_auto_20190804_0246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 4, 2, 56, 38, 127839, tzinfo=utc), verbose_name='作成日'),
        ),
    ]
