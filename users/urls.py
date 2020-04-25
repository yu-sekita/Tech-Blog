from django.urls import path

from users.views import (
    Login,
    Logout,
    PasswordReset,
    PasswordResetDone,
    PasswordResetConfirm,
    PasswordResetComplete,
    ProfileView,
    ProfileEditView,
    ProfileImageEditView,
    UserCreateView,
    UserCreateDoneView,
    UserCreateCompleteView,
)


app_name = 'users'


urlpatterns = [
    # Profile
    path('profile/<name>/', ProfileView.as_view(), name='profile'),
    path('profile/<name>/edit/',
         ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<name>/image/edit/',
         ProfileImageEditView.as_view(), name='profile_image_edit'),

    # User login
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    # User create
    # path('user_create/', UserCreateView.as_view(), name='user_create'),
    path('user_create/done/',
         UserCreateDoneView.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/',
         UserCreateCompleteView.as_view(), name='user_create_complete'),

    # Password reset
    path('password_reset/',
         PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/',
         PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/',
         PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/',
         PasswordResetComplete.as_view(), name='password_reset_complete'),

]
