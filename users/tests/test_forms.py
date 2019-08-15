import io

from django.test import TestCase
from PIL import Image


class UserCreateFormTest(TestCase):
    """ユーザー登録用フォームのテスト"""
    def test_no_data(self):
        """データ無し"""
        from users.forms import UserCreateForm

        form_data = {}
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_email(self):
        """データ有り、メールの形式に合わない"""
        from users.forms import UserCreateForm

        form_data = {
            'email': 'test_email',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_password(self):
        """データ有り、パスワードが異なる"""
        from users.forms import UserCreateForm

        form_data = {
            'email': 'test@test.com',
            'password1': 'test_password',
            'password2': 'test_password2',
        }
        form = UserCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_with_validated_data(self):
        """データ有り、バリデートが通るデータ"""
        from users.forms import UserCreateForm

        form_data = {
            'email': 'test@test.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        form = UserCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['email'], form_data.get('email'))
        self.assertEqual(
            form.cleaned_data['password1'], form_data.get('password1'))
        self.assertEqual(
            form.cleaned_data['password2'], form_data.get('password2'))


class ProfileEditFormTest(TestCase):
    """プロフィール編集用フォームのテスト"""
    def test_no_data(self):
        """データ無し"""
        from users.forms import ProfileEditForm

        form_data = {}
        form = ProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_not_user_name(self):
        """ユーザ名の空白で更新は不可能"""
        from users.forms import ProfileEditForm

        form_data = {
            'user_name': '',
            'hobby': 'Programming'
        }
        form = ProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_with_user_name(self):
        """更新可能"""
        from users.forms import ProfileEditForm

        form_data = {
            'user_name': 'Taro-Tanaka',
            'hobby': 'Programming'
        }
        form = ProfileEditForm(data=form_data)
        self.assertTrue(form.is_valid())


class ProfileImageFormTest(TestCase):
    """プロフィール画像用フォームのテスト"""
    def test_update_success(self):
        """更新成功"""
        from users.forms import ProfileImageForm

        # 画像の準備
        profile_file = io.BytesIO()
        profile_image = Image.new('RGBA', size=(480, 480), color=(256, 0, 0))
        profile_image.save(profile_file, 'png')
        profile_file.name = 'ProfileImageEditViewTest_test_ok_post.png'
        profile_file.seek(0)
        form_data = {
            'image': profile_file,
        }
        form = ProfileImageForm(data=form_data)
        self.assertTrue(form.is_valid())
