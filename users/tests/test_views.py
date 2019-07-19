from django.contrib.auth.tokens import default_token_generator
from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.models import Profile


class LoginTest(TestCase):
    """ログインviewのテスト"""
    def setUp(self):
        """ログインのためのユーザを準備"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test@test.com',
            password='password'
        )
        user.is_active = True
        user.save()

        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

    def test_get(self):
        """getリクエスト時のテスト"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_redirect_profile(self):
        """ログイン後プロフィール画面にリダイレクトされることの確認"""
        data = {
            'username': 'test@test.com',
            'password': 'password'
        }
        response = self.client.post(reverse('users:login'), data=data)
        confirm_url = reverse(
            'users:profile',
            kwargs={'name': 'testname'})
        self.assertRedirects(response, confirm_url)

    def test_relation_user_and_profile(self):
        """ユーザとプロフィールがしっかり紐づいていることの確認"""
        from django.contrib.auth import get_user_model

        # pkをずらすためユーザを作成し削除する
        User = get_user_model()
        user2 = User.objects.create_user(
            email='test2@test.com',
            password='password2')
        self.assertEqual(user2.pk, 2)
        user2.delete()

        # もう一度ユーザを作成しプロフィールと紐づける
        user3 = User.objects.create_user(
            email='test3@test.com',
            password='password3')
        self.assertEqual(user3.pk, 3)
        profile = Profile.objects.create(user=user3, user_name='profile2')
        user3.is_active = True
        user3.save()
        profile.save()

        login_data = {
            'username': 'test3@test.com',
            'password': 'password3'
        }
        response = self.client.post(reverse('users:login'), data=login_data)
        confirm_url = reverse(
            'users:profile',
            kwargs={'name': 'profile2'})
        self.assertRedirects(response, confirm_url)


class ProfileTest(TestCase):
    """プロフィールを表示するviewのテスト"""
    def test_show_profile(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(
            email='test@test.com',
            password='password'
        )
        user.is_active = True
        user.save()
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        url = reverse('users:profile', kwargs={'name': profile.user_name})
        response = self.client.get(url)

        # ステータス200
        self.assertEqual(response.status_code, 200)


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
            'user_name': 'testname',
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

    def test_ok_token_save_user(self):
        """トークンが正しく、ユーザが本登録されることの確認"""
        from django.contrib.auth import get_user_model
        from django.core.signing import dumps, loads

        from users.models import Profile

        User = get_user_model()

        # ユーザを仮登録状態で準備
        user = User.objects.create_user(email='email', password='testpassword')
        user.is_active = False
        user.save()
        # プロフィールも保存
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

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

    def test_ok_token_save_profile(self):
        """トークンが正しく、プロフィールが登録されることの確認"""
        from django.contrib.auth import get_user_model
        from django.core.signing import dumps, loads

        User = get_user_model()

        # ユーザを仮登録状態で準備
        user = User.objects.create_user(email='email', password='testpassword')
        user.is_active = False
        user.save()
        # プロフィールも保存
        profile = Profile.objects.create(user=user, user_name='testname')
        profile.save()

        # 仮登録したユーザーのトークンでリクエスト
        token = dumps(user.pk)
        url = reverse('users:user_create_complete', args=[token])
        response = self.client.get(url)

        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートuser_create_comlete.html
        self.assertTemplateUsed(response, 'users/user_create_complete.html')
        # プロフィールが保存されている
        user_pk = loads(token)
        user = User.objects.get(pk=user_pk)
        profile = Profile.objects.get(pk=user_pk)
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.user_name, 'testname')


class PasswordResetTest(TestCase):
    """パスワード変更用viewのテスト"""
    def test_get(self):
        """getリクエスト"""
        response = self.client.get(reverse('users:password_reset'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートpassword_reset.html
        self.assertTemplateUsed(response, 'users/password_reset.html')

    def test_post(self):
        """postリクエスト"""
        data = {
            'email': 'test@test.com',
        }
        response = self.client.post(reverse('users:password_reset'), data=data)
        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトpasswort_reset_done
        self.assertRedirects(response, '/password_reset/done/')


class PasswordResetDoneTest(TestCase):
    """パスワード変更用メール送信後viewのテスト"""
    def test_get(self):
        """getリクエスト"""
        response = self.client.get(reverse('users:password_reset_done'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートpassword_reset_done.html
        self.assertTemplateUsed(response, 'users/password_reset_done.html')


class PasswordResetConfirm(TestCase):
    """パスワード再入力viewのテスト"""
    def setUp(self):
        """ユーザーを登録し、uidとtokenを準備"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            email='test@test.com',
            password='test_password',
        )
        user.save()

        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

    def test_get(self):
        """getリクエスト"""
        url = reverse(
            'users:password_reset_confirm',
            kwargs={
                'uidb64': self.uid,
                'token': self.token,
            }
        )
        response = self.client.get(url)

        # getリクエスト時、
        # token部分をset-passwordに置き換えて
        # リダイレクトされることの確認
        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトpassword_reset_confirm.html
        redirect_url = reverse(
            'users:password_reset_confirm',
            kwargs={
                'uidb64': self.uid,
                'token': 'set-password',
            }
        )
        self.assertRedirects(
            response,
            redirect_url
        )

    def test_post(self):
        """postリクエスト"""

        # PasswordResetConfirmViewはget時にトークンをsessionに保存し、
        # post時にsessionのトークンをチェックしているため
        # 初めにgetリクエストを投げる
        get_url = reverse(
            'users:password_reset_confirm',
            kwargs={
                'uidb64': self.uid,
                'token': self.token,
            }
        )
        self.client.get(get_url)

        # 次にpostリクエストを投げる
        data = {
            'new_password1': 'test_password2',
            'new_password2': 'test_password2',
        }
        post_url = reverse(
            'users:password_reset_confirm',
            kwargs={
                'uidb64': self.uid,
                'token': 'set-password',
            }
        )
        response = self.client.post(post_url, data=data)
        # ステータス302
        self.assertEqual(response.status_code, 302)
        # リダイレクトpassword_reset_complete
        self.assertRedirects(
            response,
            reverse('users:password_reset_complete')
        )


class PasswordResetCompleteTest(TestCase):
    """パスワード再設定後viewのテスト"""
    def test_get(self):
        """getリクエストのテスト"""
        response = self.client.get(reverse('users:password_reset_complete'))
        # ステータス200
        self.assertEqual(response.status_code, 200)
        # テンプレートpassword_reset_complete.html
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')
