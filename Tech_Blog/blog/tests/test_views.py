import uuid

from django.test import TestCase
from django.urls import reverse

from blog.models import Article


class ArticleListViewTest(TestCase):
    """記事を表示するviewのテスト"""
    def test_no_article(self):
        """記事が何も作られていないことの確認"""
        response = self.client.get(reverse('blog:index'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートindex.html
        self.assertTemplateUsed(response, 'blog/index.html')
        # オブジェクトが0
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_one_article(self):
        """記事が1つ作られている場合の確認"""
        Article.objects.create(title='Test1', text='Test1 text')

        response = self.client.get(reverse('blog:index'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートindex.html
        self.assertTemplateUsed(response, 'blog/index.html')
        # オブジェクトArticleが1つ
        self.assertQuerysetEqual(response.context['articles'],
                                 ['<Article: Test1>', ])

    def test_two_article(self):
        """記事が2つ作られている場合の確認"""
        Article.objects.create(title='Test1', text='Test1 text')
        Article.objects.create(title='Test2', text='Test2 text')

        response = self.client.get(reverse('blog:index'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートindex.html
        self.assertTemplateUsed(response, 'blog/index.html')
        # オブジェクトArticleが2つ
        self.assertQuerysetEqual(
            response.context['articles'],
            [
                '<Article: Test1>',
                '<Article: Test2>'
            ],
            ordered=False
        )


class ArticleCreateViewTest(TestCase):
    """記事を追加するviewのテスト"""
    def test_get(self):
        """getリクエスト時のテスト"""
        response = self.client.get(reverse('blog:create'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートcreate.html
        self.assertTemplateUsed(response, 'blog/create.html')

    def test_no_dada(self):
        """空のデータでpost時のテスト"""
        data = {}
        response = self.client.post(reverse('blog:create'), data=data)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートcreate.html
        self.assertTemplateUsed(response, 'blog/create.html')

    def test_with_dada(self):
        """データ有りpost時のテスト"""
        data = {
            'title': 'Test1',
            'text': 'Test1 text'
        }
        response = self.client.post(reverse('blog:create'), data=data)
        # ステータス302
        self.assertEqual(response.status_code, 302)

        # DBに登録されていることの確認
        articles = Article.objects.all()
        self.assertEqual(articles[0].title, 'Test1')
        self.assertEqual(articles.count(), 1)


class ArticleDetailViewTest(TestCase):
    """記事の詳細を表示するviewのテスト"""
    def test_no_data(self):
        """空のデータでget時のテスト"""
        url = reverse('blog:detail', args=(uuid.uuid4(), ))
        response = self.client.get(url)
        # ステータス404
        self.assertEqual(response.status_code, 404)

    def test_one_data(self):
        """1件のデータがある時のテスト"""
        article = Article.objects.create(title='test1', text='test text1')
        url = reverse('blog:detail', args=(article.id, ))

        response = self.client.get(url)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートdetail.html
        self.assertTemplateUsed(response, 'blog/detail.html')
        self.assertContains(response, article.title)
