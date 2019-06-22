from django.core.mail import outbox
from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse


class UserCreateViewTest(TestCase):
    """ユーザの仮登録をするviewのテスト"""
    def test_get(self):
        """getリクエスト時のテスト"""
        response = self.client.get(reverse('users:user_create'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートuser_create.html
        self.assertTemplateUsed(response, 'users/user_create.html')

    def test_no_data(self):
        """postリクエスト時、データがない時のテスト"""
        data = {}
        response = self.client.post(reverse('users:user_create'), data=data)
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートuser_create.html
        self.assertTemplateUsed(response, 'users/user_create.html')

    def test_with_data(self):
        """postリクエスト時、データ有りのテスト"""
        data = {
            'email': 'test@test.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        response = self.client.post(reverse('users:user_create'), data=data)
        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトuser_create_done
        self.assertRedirects(response, '/user_create/done/')


class UserCreateCompleteViewTest(TestCase):
    """ユーザの本登録をするviewのテスト"""
    def test_ng_token(self):
        """トークンが正しくない場合の確認"""
        token = 'test'
        url = reverse('users:user_create_complete', args=[token])
        response = self.client.get(url)
        # ステータス400
        self.assertEqual(response.status_code, 400)

    def test_deleted_user(self):
        """仮登録後、ユーザを削除した場合の確認"""
        from django.contrib.auth import get_user_model
        from django.core.signing import dumps

        User = get_user_model()

        # ユーザを仮登録状態で準備
        user = User.objects.create_user(email='email', password='testpassword')
        user.is_active = False
        user.save()

        # 仮登録したユーザーのトークンを取得
        token = dumps(user.pk)
        # ユーザーを削除して、リクエストを投げる
        user.delete()
        url = reverse('users:user_create_complete', args=[token])
        response = self.client.get(url)

        # ステータス400
        self.assertEqual(response.status_code, 400)

    def test_actived_user(self):
        """ユーザがアクティブ状態で本登録した時の確認"""
        from django.contrib.auth import get_user_model
        from django.core.signing import dumps

        User = get_user_model()

        # ユーザを本登録状態で準備
        user = User.objects.create_user(email='email', password='testpassword')
        user.is_active = True
        user.save()

        # 本登録したユーザーのトークンでリクエスト
        token = dumps(user.pk)
        url = reverse('users:user_create_complete', args=[token])
        response = self.client.get(url)

        # ステータス400
        self.assertEqual(response.status_code, 400)

    def test_ok_token(self):
        """トークンが正しく、ユーザが本登録されることの確認"""
        from django.contrib.auth import get_user_model
        from django.core.signing import dumps, loads

        User = get_user_model()

        # ユーザを仮登録状態で準備
        user = User.objects.create_user(email='email', password='testpassword')
        user.is_active = False
        user.save()

        # 仮登録したユーザーのトークンでリクエスト
        token = dumps(user.pk)
        url = reverse('users:user_create_complete', args=[token])
        response = self.client.get(url)

        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートuser_create_comlete.html
        self.assertTemplateUsed(response, 'users/user_create_complete.html')
        # ユーザのis_activeがTrue
        user_pk = loads(token)
        user = User.objects.get(pk=user_pk)
        self.assertTrue(user.is_active)
