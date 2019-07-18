from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import ugettext as _


class UserManager(BaseUserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """権限を全てFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは全ての権限をTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル"""
    email = models.EmailField(_('email address'), unique=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        )
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now()
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ユーザーにメールを送る"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性にアクセスした場合にメールアドレスを返す"""
        return self.email


GENDER_CHOICES = (
    ('1', '男性'),
    ('2', '女性'),
)


class Profile(models.Model):
    """ユーザーに紐付くプロフィール"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    description = models.TextField(blank=True)
    gender = models.CharField(
        "性別",
        max_length=2,
        choices=GENDER_CHOICES,
        blank=True
    )
    link = models.CharField('Link', max_length=255, blank=True)
    hobby = models.CharField('Hobby', max_length=255, blank=True)
    image = models.ImageField(upload_to='media/profile', blank=True)

    def __str__(self):
        fullname = self.get_full_name()
        return self.user.email if fullname is None else fullname

    def get_full_name(self):
        """first_nameとlast_nameをスペースで繋げて返す"""
        if self.first_name is None and self.last_name is None:
            return None
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """ユーザーのshort nameを返す"""
        return self.first_name

    def get_absolute_url(self):
        """ユーザー更新時の戻り先URL"""
        fullname = self.get_full_name()
        name = self.user.email if fullname is None else fullname
        return reverse('users:profile', kwargs={'name': name})
