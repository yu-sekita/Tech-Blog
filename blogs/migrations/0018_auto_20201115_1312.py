# Generated by Django 2.2.10 on 2020-11-15 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0017_auto_20200412_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='作成日'),
        ),
    ]