from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from blogs.forms import ArticleForm
from blogs.models import Article


def _set_full_name(context, user):
    """ユーザーのフルネームがあればコンテキストに設定"""
    if user and user.is_authenticated:
        context['name'] = user.get_full_name()


def _escape(un_escaped_text):
    """エスケープ"""
    un_escaped_text = un_escaped_text.replace('<', '&lt;')
    un_escaped_text = un_escaped_text.replace('>', '&gt;')
    un_escaped_text = un_escaped_text.replace('\"', '&quot;')
    un_escaped_text = un_escaped_text.replace('\'', '&#39;')
    escaped_text = un_escaped_text.replace('&', '&amp;')
    return escaped_text


class ArticleListView(generic.ListView):
    """記事の一覧を表示するview"""
    model = Article
    context_object_name = 'articles'
    template_name = 'blogs/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _set_full_name(context, self.request.user)
        return context


class ArticleCreateView(LoginRequiredMixin, generic.CreateView):
    """記事を追加するview"""
    model = Article
    form_class = ArticleForm
    template_name = 'blogs/create.html'

    def form_valid(self, form):
        """記事とユーザーを紐付ける"""
        if self.request.user.is_authenticated:
            # エスケープ
            escaped_text = _escape(form.instance.text)
            form.instance.text = escaped_text
            form.instance.author = self.request.user
        return super(generic.CreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _set_full_name(context, self.request.user)
        return context


class ArticleDetailView(generic.DetailView):
    """記事の詳細を表示するview"""
    model = Article
    context_object_name = 'article'
    template_name = 'blogs/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _set_full_name(context, self.request.user)
        return context
