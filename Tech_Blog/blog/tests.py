from django.test import TestCase

from blog.models import Article


class ArticleTest(TestCase):
    def setUp(self):
        Article.objects.bulk_create([
            Article(title='Test1', text='Test1 text'),
            Article(title='Test2', text='Test2 text'),
            Article(title='Test3', text='Test3 text')
        ])

    def test_create_article(self):
        result = Article.objects.all().count()
        self.assertEqual(result, 3)
