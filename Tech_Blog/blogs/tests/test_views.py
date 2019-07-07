import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from blogs.models import Article
from blogs.views import _set_full_name


User = get_user_model()


class SetFullNameTest(TestCase):
    """コンテキストにユーザーのフルネームを設定する関数のテスト"""
    def test_no_user(self):
        """ユーザーがいない時の確認"""
        context = {}
        _set_full_name(context, None)
        self.assertEqual(context.get('name'), None)

    def test_no_fullname(self):
        """フルネームがないユーザーの確認"""
        context = {}
        user = User.objects.create_user(email="test@t.com", password="passwor")
        user.is_active = True

        _set_full_name(context, user)
        self.assertEqual(context.get('name'), '')

    def test_with_fullname(self):
        """フルネームがあるユーザーの確認"""
        context = {}
        user = User.objects.create_user(email="test@t.com", password="passwor")
        user.is_active = True
        user.first_name = 'Potter'
        user.last_name = 'Harry'

        _set_full_name(context, user)
        self.assertEqual(context.get('name'), user.get_full_name())


class ArticleListViewTest(TestCase):
    """記事を表示するviewのテスト"""
    def test_no_article(self):
        """記事が何も作られていないことの確認"""
        response = self.client.get(reverse('blogs:index'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートindex.html
        self.assertTemplateUsed(response, 'blogs/index.html')
        # オブジェクトが0
        self.assertQuerysetEqual(response.context['articles'], [])

    def test_one_article(self):
        """記事が1つ作られている場合の確認"""
        Article.objects.create(title='Test1', text='Test1 text')

        response = self.client.get(reverse('blogs:index'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートindex.html
        self.assertTemplateUsed(response, 'blogs/index.html')
        # オブジェクトArticleが1つ
        self.assertQuerysetEqual(response.context['articles'],
                                 ['<Article: Test1>', ])

    def test_two_article(self):
        """記事が2つ作られている場合の確認"""
        Article.objects.create(title='Test1', text='Test1 text')
        Article.objects.create(title='Test2', text='Test2 text')

        response = self.client.get(reverse('blogs:index'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートindex.html
        self.assertTemplateUsed(response, 'blogs/index.html')
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
        # ユーザを準備
        user = User.objects.create_user(
            email='test@test.com',
            password='test_password'
        )
        user.is_active = True
        self.client.login(email='test@test.com', password='test_password')

        response = self.client.get(reverse('blogs:create'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートcreate.html
        self.assertTemplateUsed(response, 'blogs/create.html')

    def test_no_dada(self):
        """空のデータでpost時のテスト"""
        # ユーザを準備
        user = User.objects.create_user(
            email='test@test.com',
            password='test_password'
        )
        user.is_active = True
        self.client.login(email='test@test.com', password='test_password')

        data = {}
        response = self.client.post(reverse('blogs:create'), data=data)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートcreate.html
        self.assertTemplateUsed(response, 'blogs/create.html')
        # DBに登録されていないことの確認
        articles = Article.objects.all()
        self.assertEqual(articles.count(), 0)

    def test_not_login(self):
        """ユーザーがログインをしていない状態でpost"""
        data = {
            'title': 'Test1',
            'text': 'Test1 text',
        }
        response = self.client.post(reverse('blogs:create'), data=data)
        # ステータス302
        self.assertEqual(response.status_code, 302)
        # テンプレートcreate.html
        self.assertRedirects(response, '/login/?next=/create/')
        # DBに登録されていないことの確認
        articles = Article.objects.all()
        self.assertEqual(articles.count(), 0)

    def test_with_dada(self):
        """データ有りpost時のテスト"""
        data = {
            'title': 'Test1',
            'text': 'Test1 text',
        }

        # ユーザを準備
        user = User.objects.create_user(
            email='test@test.com',
            password='test_password'
        )
        user.is_active = True
        self.client.login(email='test@test.com', password='test_password')

        response = self.client.post(reverse('blogs:create'), data=data)

        # ステータス302
        self.assertEqual(response.status_code, 302)

        # DBに登録されていることの確認
        articles = Article.objects.all()
        self.assertEqual(articles[0].title, 'Test1')
        self.assertEqual(articles.count(), 1)

    def test_danger_data(self):
        """textにscriptタグがある場合のテスト"""

        test_text = '''test
        <script> alert('test xss') </script>'''

        confirm_text = '''test
        &lt;script&gt; alert('test xss') &lt;/script&gt;'''

        data = {
            'title': 'Test1',
            'text': test_text,
        }

        # ユーザを準備
        user = User.objects.create_user(
            email='test@test.com',
            password='test_password'
        )
        user.is_active = True
        self.client.login(email='test@test.com', password='test_password')

        response = self.client.post(reverse('blogs:create'), data=data)

        # textはエスケープされてDBに登録されていることの確認
        articles = Article.objects.all()
        self.assertEqual(articles[0].text, confirm_text)
        # ユーザが紐づいていることの確認
        self.assertEqual(articles[0].author.email, user.email)


class ArticleDetailViewTest(TestCase):
    """記事の詳細を表示するviewのテスト"""
    def test_no_data(self):
        """空のデータでget時のテスト"""
        url = reverse('blogs:detail', args=(uuid.uuid4(), ))
        response = self.client.get(url)
        # ステータス404
        self.assertEqual(response.status_code, 404)

    def test_one_data(self):
        """1件のデータがある時のテスト"""
        article = Article.objects.create(title='test1', text='test text1')
        url = reverse('blogs:detail', args=(article.id, ))

        response = self.client.get(url)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートdetail.html
        self.assertTemplateUsed(response, 'blogs/detail.html')
        self.assertContains(response, article.title)
