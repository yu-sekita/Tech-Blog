import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from markdownx.models import MarkdownxField


User = get_user_model()


class Category(models.Model):
    """カテゴリー"""
    name = models.CharField('カテゴリー名', max_length=255, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    """記事"""
    # pkにuuidを使う
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('タイトル', max_length=255)
    # Markdown形式
    text = MarkdownxField('本文')
    created_at = models.DateTimeField('作成日', default=timezone.now())
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    is_public = models.BooleanField('公開', default=True)
    thumbnail = models.ImageField(upload_to='thumbnail', blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    # SEO
    title_for_seo = models.CharField('タイトル', max_length=255, null=True)
    description = models.TextField(null=True)
    keywords = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """更新完了時の戻り先URL"""
        return reverse('blogs:article_detail', kwargs={'pk': self.id})
