from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import User, UserManager


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

    def test_get_name(self):
        """ショート、フルネームが取得できることの確認"""
        User = get_user_model()
        data = {
            'email': 'testuser@test.com',
            'password': 'test_password',
            'first_name': '田中',
            'last_name': '太郎'
        }
        user = User.objects.create_user(**data)
        full_name = '%s %s' % (data.get('first_name'), data.get('last_name'))
        self.assertEqual(user.get_full_name(), full_name)
        short_name = data.get('first_name')
        self.assertEqual(user.get_short_name(), short_name)
        email = data.get('email')
        self.assertEqual(user.username, email)
