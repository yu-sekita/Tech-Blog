# Generated by Django 2.2.1 on 2019-05-26 04:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 5, 26, 4, 24, 13, 663560, tzinfo=utc), verbose_name='作成日'),
        ),
    ]
