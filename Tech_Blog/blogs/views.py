from django.views import generic

from blogs.forms import ArticleForm
from blogs.models import Article


class ArticleListView(generic.ListView):
    """記事の一覧を表示するview"""
    model = Article
    context_object_name = 'articles'
    template_name = 'blogs/index.html'


class ArticleCreateView(generic.CreateView):
    """記事を追加するview"""
    model = Article
    form_class = ArticleForm
    template_name = 'blogs/create.html'


class ArticleDetailView(generic.DetailView):
    """記事の詳細を表示するview"""
    model = Article
    context_object_name = 'article'
    template_name = 'blogs/detail.html'
