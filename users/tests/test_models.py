from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import (
    GENDER_CHOICES, Profile, User, UserManager
)


class UserManagerTest(TestCase):
    """ユーザーマネージャーのテスト"""
    def test_createuser_mail_blank(self):
        """メールアドレスブランクで登録し、エラーハンドリングされている確認"""
        User = get_user_model()
        data = {
            'email': '',
            'password': 'test_password'
        }
        with self.assertRaises(ValueError) as error:
            User.objects.create_user(**data)
        error_message = 'The given email must be set'
        self.assertEquals(error.exception.args[0], error_message)

    def test_createuser_mail_none(self):
        """メールアドレスなしで登録し、エラーハンドリングされている確認"""
        User = get_user_model()
        data = {
            'email': None,
            'password': 'test_password'
        }
        with self.assertRaises(ValueError) as error:
            User.objects.create_user(**data)
        error_message = 'The given email must be set'
        self.assertEquals(error.exception.args[0], error_message)

    def test_createuser(self):
        """パスワードブランクで登録できることの確認"""
        User = get_user_model()
        data = {
            'email': 'test@test.com',
            'password': '',

        }
        user = User.objects.create_user(**data)
        self.assertEqual(user.email, data.get('email'))

    def test_createuser_permission_false(self):
        """ユーザー登録時、権限は全てFalseで登録されていることの確認"""
        User = get_user_model()
        data = {
            'email': 'test@test.com',
            'password': 'test_password'
        }
        user = User.objects.create_user(**data)
        self.assertEqual(user.email, data.get('email'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_createuser_permission_false(self):
        """スーパーユーザー登録時、権限は全てTrueで登録されていることの確認"""
        User = get_user_model()
        data = {
            'email': 'testsuper@test.com',
            'password': 'test_password'
        }
        user = User.objects.create_superuser(**data)
        self.assertEqual(user.email, data.get('email'))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class ProfileTest(TestCase):
    """ユーザーに紐付くプロフィールのテスト"""
    def test_not_register(self):
        """データが１件もない場合のテスト"""
        profiles = Profile.objects.all()
        self.assertEqual(profiles.count(), 0)

    def test_registed(self):
        """データが作られた場合のテスト"""
        User = get_user_model()
        user = User.objects.create(email='test@test.com', password='testpass')
        Profile.objects.create(
            user=user,
            user_name='Taro-Tanaka',
            description="I'm a python programmer. This site made by Django",
            gender=GENDER_CHOICES[0],
            link='http://test.com',
            hobby='playing soccer, programming python',
        )

        profiles = Profile.objects.all()
        self.assertEqual(profiles.count(), 1)
        profile = profiles[0]
        self.assertEqual(profile.user_name, 'Taro-Tanaka')

    def test_absolute_url(self):
        """更新完了時の戻り先URLを正しく取得できることの確認"""
        User = get_user_model()
        user = User.objects.create(email='test@test.com', password='testpass')
        Profile.objects.create(
            user=user,
            user_name='Taro-Tanaka',
            description="I'm a python programmer. This site made by Django",
            gender=GENDER_CHOICES[0],
            link='http://test.com',
            hobby='playing soccer, programming python',
        )

        profile = Profile.objects.get(user=user)
        confirm_url = reverse('users:profile', kwargs={'name': 'Taro-Tanaka'})
        self.assertEqual(profile.get_absolute_url(), confirm_url)
