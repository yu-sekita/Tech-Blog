from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from blogs.escape import escape_tag
from blogs.forms import ArticleForm
from blogs.models import Article
from users.models import Profile


ACCEPT_TAGS = [
    'b', 'blockquote', 'code', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'ol', 'ol start="42"', 'p', 'pre', 'sub', 'sup', 'strong',
    'strike', 'ul', 'br', 'hr',
]


def _set_full_name(context, user):
    """ユーザーのフルネームがあればコンテキストに設定"""
    profile = Profile.objects.get(pk=user.pk)
    name = profile.get_full_name()
    context['name'] = name if name is not None else ''


class ArticleListView(generic.ListView):
    """記事の一覧を表示するview"""
    model = Article
    context_object_name = 'articles'
    template_name = 'blogs/index.html'
    paginate_by = 12

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
            # ACCEPT_TAGSに登録していないタグをエスケープ
            escaped_text = escape_tag(form.instance.text, ACCEPT_TAGS)
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
