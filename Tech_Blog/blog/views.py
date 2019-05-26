from django.views import generic

from blog.models import Article


class ArticleListView(generic.ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'blog/index.html'
