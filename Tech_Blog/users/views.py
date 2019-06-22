from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import (
    BadSignature,
    dumps,
    loads,
    SignatureExpired,
)
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import get_template
from django.views import generic

from users.forms import (
    LoginForm,
    UserCreateForm,
)


User = get_user_model()


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    """ユーザのプロフィールを表示"""
    template_name = 'users/profile.html'


class Login(LoginView):
    """ログイン"""
    form_class = LoginForm
    template_name = 'users/login.html'


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