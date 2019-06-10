from django.urls import path

from blogs import views


app_name = 'blogs'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='index'),
    path('create/', views.ArticleCreateView.as_view(), name='create'),
    path('detail/<uuid:pk>/',
         views.ArticleDetailView.as_view(),
         name='detail'),
]
