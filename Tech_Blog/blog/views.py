from django.urls import reverse_lazy
from django.views import generic

from blog.forms import ArticleForm
from blog.models import Article


class ArticleListView(generic.ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'blog/index.html'


class ArticleCreateView(generic.CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/create.html'
