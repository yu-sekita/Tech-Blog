from django.urls import path

from blog import views


app_name = 'blog'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='index'),
    path('create/', views.ArticleCreateView.as_view(), name='create')
]
