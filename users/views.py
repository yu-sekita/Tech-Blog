from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import (
    BadSignature, dumps, loads, SignatureExpired,
)
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.views import generic

from users.forms import (
    LoginForm, MyPasswordResetForm, MySetPasswordForm, ProfileEditForm,
    UserCreateForm,
)
from users.models import Profile


User = get_user_model()


class ProfileView(generic.TemplateView):
    """ユーザのプロフィールを表示"""
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        """プロフィールを表示"""
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        return context


class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    """プロフィール編集"""
    model = Profile
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'

    def get_object(self):
        """URLにpkを含まないため"""
        return Profile.objects.get(user=self.request.user)


class Login(LoginView):
    """ログイン"""
    form_class = LoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        next_url = self.get_redirect_url()
        if next_url:
            return '%s' % (next_url)
        else:
            profile = Profile.objects.get(user=self.request.user)
            redirect_url = reverse(
                'users:profile',
                kwargs={'name': profile.user_name})
            return redirect_url


class Logout(LogoutView):
    """ログアウト"""
    template_view = 'users/logout.html'


class UserCreateView(generic.CreateView):
    """ユーザーの仮登録"""
    template_name = 'users/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行"""
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # プロフィールも一緒に作成
        profile = Profile.objects.create(
            user=user,
            user_name=form.cleaned_data['user_name'])
        profile.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject_template = get_template('users/mail/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('users/mail/create/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('users:user_create_done')


class UserCreateDoneView(generic.TemplateView):
    """仮登録後のページを表示"""
    template_name = 'users/user_create_done.html'


class UserCreateCompleteView(generic.TemplateView):
    """ユーザーの本登録"""
    template_name = 'users/user_create_complete.html'
    # １日以内
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self, request, **kwargs):
        """tokenが正しければ本登録"""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)

            # ユーザーがいない
            except User.DoesNotExist:
                return HttpResponseBadRequest()

            else:
                if not user.is_active:
                    # 問題がなければ本登録
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class PasswordReset(PasswordResetView):
    """パスワード変更用URLを送る"""
    subject_template_name = 'users/mail/password_reset/subject.txt'
    email_template_name = 'users/mail/password_reset/message.txt'
    template_name = 'users/password_reset.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLの送付後"""
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新しいパスワードの入力"""
    form_class = MySetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetComplete(PasswordResetCompleteView):
    """新しいパスワードの入力完了"""
    template_name = 'users/password_reset_complete.html'
