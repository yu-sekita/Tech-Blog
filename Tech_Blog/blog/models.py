from django.db import models
from django.utils import timezone


class Article(models.Model):
    """記事"""
    title = models.CharField('タイトル', max_length=255)
    text = models.TextField('本文')
    created_at = models.DateTimeField('作成日', default=timezone.now())

    def __str__(self):
        return self.title
