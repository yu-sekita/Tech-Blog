# Generated by Django 2.2.3 on 2019-08-04 02:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20190724_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='profile'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 4, 2, 46, 32, 255153, tzinfo=utc), verbose_name='date joined'),
        ),
    ]
