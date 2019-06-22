from django.test import TestCase

from users.forms import UserCreateForm


class UserCreateFormTest(TestCase):
    """ユーザー登録用フォームのテスト"""
    def test_no_data(self):
        """データ無し"""
        form_data = {}
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_email(self):
        """データ有り、メールの形式に合わない"""
        form_data = {
            'email': 'test_email',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_password(self):
        """データ有り、パスワードが異なる"""
        form_data = {
            'email': 'test@test.com',
            'password1': 'test_password',
            'password2': 'test_password2',
        }
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_with_validated_data(self):
        """データ有り、バリデートが通るデータ"""
        form_data = {
            'email': 'test@test.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        form = UserCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], form_data.get('email'))
