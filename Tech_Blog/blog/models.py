import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from markdownx.models import MarkdownxField


class Article(models.Model):
    """記事"""
    # pkにuuidを使う
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('タイトル', max_length=255)
    # Markdown形式
    text = MarkdownxField('本文')
    created_at = models.DateTimeField('作成日', default=timezone.now())

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """更新完了時の戻り先URL"""
        return reverse('blog:index')
