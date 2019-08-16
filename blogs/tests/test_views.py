import datetime
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from blogs.models import Article
from blogs.views import _set_full_name
from users.models import Profile


User = get_user_model()


class SetFullNameTest(TestCase):
    """コンテキストにユーザーのフルネームを設定する関数のテスト"""
    def test_no_user(self):
        """ユーザーがいない時の確認"""
        context = {}
        _set_full_name(context, None)
        self.assertEqual(context.get('user_name'), '')

    def test_no_username(self):
        """フルネームがないユーザーの確認"""
        user = User.objects.create_user(
            email="test@test.com", password="password")
        user.is_active = True
        profile = Profile.objects.create(user=user, user_name='')
        profile.save()

        context = {}
        _set_full_name(context, user)
        self.assertEqual(context.get('user_name'), '')

    def test_with_fullname(self):
        """フルネームがあるプロフィールの確認"""
        user = User.objects.create_user(
            email="test@test.com", password="password")
        user.is_active = True
        user.save()
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        context = {}
        _set_full_name(context, user)
        self.assertEqual(context.get('user_name'), 'testname')


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

    def test_with_private_aritcle(self):
        """非公開記事がある場合のテスト"""
        Article.objects.bulk_create([
            Article(title='title1', text='text1'),
            Article(title='title2', text='text2', is_public=False),
        ])

        response = self.client.get(reverse('blogs:index'))
        # 公開記事のみ表示
        self.assertEqual(response.context['articles'].count(), 1)
        self.assertEqual(response.context['articles'][0].title, 'title1')
        self.assertTrue(response.context['articles'][0].is_public)

    def test_orderd(self):
        """作成日時の降順で出力されることの確認"""
        # 一番新しい記事
        time = timezone.now() + datetime.timedelta(days=30)
        Article.objects.create(title='first', text='1', created_at=time)
        # 一番古い記事
        time = timezone.now() + datetime.timedelta(days=10)
        Article.objects.create(title='third', text='3', created_at=time)
        # ２番目に新しい記事
        time = timezone.now() + datetime.timedelta(days=20)
        Article.objects.create(title='second', text='2', created_at=time)

        response = self.client.get(reverse('blogs:index'))
        result = response.context['articles']
        self.assertEqual(result[0].text, '1')
        self.assertEqual(result[1].text, '2')
        self.assertEqual(result[2].text, '3')


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
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        response = self.client.get(reverse('blogs:article_create'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートarticle_create.html
        self.assertTemplateUsed(response, 'blogs/article_create.html')

    def test_no_dada(self):
        """空のデータでpost時のテスト"""
        # ユーザを準備
        user = User.objects.create_user(
            email='test@test.com',
            password='test_password'
        )
        user.is_active = True
        self.client.login(email='test@test.com', password='test_password')
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        data = {}
        response = self.client.post(reverse('blogs:article_create'), data=data)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートarticle_create.html
        self.assertTemplateUsed(response, 'blogs/article_create.html')
        # DBに登録されていないことの確認
        articles = Article.objects.all()
        self.assertEqual(articles.count(), 0)

    def test_not_login(self):
        """ユーザーがログインをしていない状態でpost"""
        data = {
            'title': 'Test1',
            'text': 'Test1 text',
        }
        response = self.client.post(reverse('blogs:article_create'), data=data)
        # ステータス302
        self.assertEqual(response.status_code, 302)
        # テンプレートarticle_create.html
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
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        response = self.client.post(reverse('blogs:article_create'), data=data)

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
        &lt;script&gt; alert(&#39;test xss&#39;) &lt;/script&gt;'''

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
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        self.client.post(reverse('blogs:article_create'), data=data)

        # textはエスケープされてDBに登録されていることの確認
        articles = Article.objects.all()
        self.assertEqual(articles[0].text, confirm_text)
        # ユーザが紐づいていることの確認
        self.assertEqual(articles[0].author.email, user.email)


class ArticleDetailViewTest(TestCase):
    """記事の詳細を表示するviewのテスト"""
    def setUp(self):
        # ユーザを準備
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test_password'
        )
        self.user.is_active = True
        self.user.save()
        # プロフィールを準備
        profile = Profile.objects.create(
            user=self.user,
            user_name='testname'
        )
        profile.save()

    def test_no_data(self):
        """空のデータでget時のテスト"""
        url = reverse('blogs:article_detail', args=(uuid.uuid4(), ))
        response = self.client.get(url)
        # ステータス404
        self.assertEqual(response.status_code, 404)

    def test_one_data(self):
        """1件のデータがある時のテスト"""
        article = Article.objects.create(
            title='test1',
            text='test text1',
            author=self.user)
        url = reverse('blogs:article_detail', args=(article.id, ))

        response = self.client.get(url)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートarticle_detail.html
        self.assertTemplateUsed(response, 'blogs/article_detail.html')
        self.assertContains(response, article.title)

    def test_get_context_data(self):
        """コンテキストデータが正常に渡されていることの確認"""
        article = Article.objects.create(
            title='test1',
            text='test text1',
            author=self.user)
        url = reverse('blogs:article_detail', args=(article.id, ))

        response = self.client.get(url)

        # コンテキスト
        self.assertTrue(response.context['author_name'] is not None)


class ArticleEditViewTest(TestCase):
    """記事編集viewのテスト"""
    def setUp(self):
        # ユーザを保存
        user = User.objects.create_user(
            email='test@test.com',
            password='testpass'
        )
        user.is_active = True
        user.save()

        # プロフィールを保存
        profile = Profile.objects.create(
            user=user,
            user_name='test name'
        )
        profile.save()

        # 記事を保存
        article = Article.objects.create(
            title='test title',
            text='test text',
            author=user
        )
        article.save()

        # id
        self.id = article.id
        # URL
        self.url = reverse('blogs:article_edit', args=(self.id, ))

    def test_not_login_get(self):
        """未ログインでgetリクエストした場合のテスト"""
        response = self.client.get(self.url)

        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトlogin
        confirm_redirect = '/login/?next=%2Fedit%2F' + str(self.id) + '/'
        self.assertRedirects(response, confirm_redirect)

    def test_not_author_edit_get(self):
        """投稿者でないユーザーがgetリクエスト投げた場合のテスト"""
        not_author = User.objects.create_user(
            email='test2@test.com',
            password='testpass'
        )
        not_author.is_active = True
        not_author.save()

        # ログイン
        self.client.login(email='test2@test.com', password='testpass')
        # getリクエストを投げる
        response = self.client.get(self.url)

        # ステータス400
        self.assertEqual(response.status_code, 400)

    def test_ok_get(self):
        """getリクエストが成功する場合のテスト"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        response = self.client.get(self.url)

        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートblogs/article_edit.html
        self.assertTemplateUsed(response, 'blogs/article_edit.html')

    def test_not_login_post(self):
        """未ログインでpostリクエストした場合のテスト"""
        form_data = {
            'title': 'test title',
            'text': 'rename test text2'
        }

        response = self.client.post(self.url, data=form_data)

        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトlogin
        confirm_redirect = '/login/?next=%2Fedit%2F' + str(self.id) + '/'
        self.assertRedirects(response, confirm_redirect)

    def test_empty_title_post(self):
        """タイトルが空文字でpostリクエストした場合のテスト"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        form_data = {
            'title': '',
            'text': 'rename test text2'
        }

        response = self.client.post(self.url, data=form_data)

        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートblogs/article_edit.html
        self.assertTemplateUsed(response, 'blogs/article_edit.html')

    def test_empty_text_post(self):
        """本文が空文字でpostリクエストした場合のテスト"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        form_data = {
            'title': 'rename test title',
            'text': ''
        }

        response = self.client.post(self.url, data=form_data)

        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートblogs/article_edit.html
        self.assertTemplateUsed(response, 'blogs/article_edit.html')

    def test_ok_post(self):
        """postリクエストが成功する場合のテスト"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        form_data = {
            'title': 'rename test title2',
            'text': 'rename test text2'
        }

        response = self.client.post(self.url, data=form_data)

        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトarticle_detail
        confirm_redirect = '/detail/' + str(self.id) + '/'
        self.assertRedirects(response, confirm_redirect)


class ArticleDeleteViewTest(TestCase):
    """記事削除機能のテスト"""
    def setUp(self):
        # ユーザ準備
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='testpass'
        )
        self.user.is_active = True
        self.user.save()
        # プロフィール準備
        profile = Profile.objects.create(
            user=self.user,
            user_name='testname'
        )
        profile.save()
        # 記事準備
        article = Article.objects.create(
            title='test title',
            text='test text',
            author=self.user
        )
        article.save()
        # url準備
        self.article_id = article.pk
        self.url = reverse('blogs:article_delete', args=(self.article_id, ))

    def test_get_not_login(self):
        """未ログインユーザから遷移した場合のテスト"""
        # getリクエスト
        response = self.client.get(self.url)

        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクト
        confirm_url = '/login/?next=/delete/' + str(self.article_id) + '/'
        self.assertRedirects(
            response,
            confirm_url
        )

    def test_get_not_author(self):
        """投稿者でないユーザから遷移した場合のテスト"""
        # 投稿者でないユーザの準備
        not_author = get_user_model().objects.create_user(
            email='notauthor@test.com',
            password='notauthor'
        )
        not_author.is_active = True
        not_author.save()

        # 投稿者でないユーザでログイン
        self.client.login(email='notauthor@test.com', password='notauthor')

        # getリクエスト
        response = self.client.get(self.url)

        # BadRequest
        self.assertEqual(response.status_code, 400)

    def test_context_data(self):
        """コンテキストデータが正しく渡されていることの確認"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        # getリクエスト
        response = self.client.get(self.url)

        # ステータス200
        self.assertEqual(response.status_code, 200)
        # コンテキストデータ
        self.assertEqual(response.context['article_title'], 'test title')

    def test_success_url(self):
        """削除成功時、正しく遷移されることの確認"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        # postリクエスト
        response = self.client.post(self.url)

        # ステータス200
        self.assertEqual(response.status_code, 302)
        # リダイレクト
        self.assertRedirects(response, '/profile/testname/')

    def test_delete_article(self):
        """削除成功時、記事が削除されていることの確認"""
        # ログイン
        self.client.login(email='test@test.com', password='testpass')

        # postリクエスト
        self.client.post(self.url)

        # 記事が存在しない
        aritlces = Article.objects.all()
        self.assertEqual(len(aritlces), 0)
