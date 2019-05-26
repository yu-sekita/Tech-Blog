from django.urls import path

from blog import views


urlpatterns = [
    path('', views.ArticleListView.as_view(), name='index')
]
