from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm,
)


User = get_user_model()


class LoginForm(AuthenticationForm):
    """ログイン用のフォーム"""

    def __init__(self, *args, **kwargs):
        """Bootstrap4に対応させる"""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserCreateForm(UserCreationForm):
    """ユーザー登録用のフォーム"""

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        """Bootstrap4に対応させる"""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        """仮登録段階のユーザーを消去"""
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れた時用のフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """パスワード忘れた時用のパスワード再設定用フォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
