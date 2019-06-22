from django.urls import path

from users.views import (
    Login,
    Logout,
    ProfileView,
    UserCreateView,
    UserCreateDoneView,
    UserCreateCompleteView,
)


app_name = 'users'


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('user_create/', UserCreateView.as_view(), name='user_create'),
    path('user_create/done/',
         UserCreateDoneView.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/',
         UserCreateCompleteView.as_view(), name='user_create_complete'),
]
