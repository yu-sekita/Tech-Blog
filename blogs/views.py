from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from blogs.escape import escape_markdown
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
    if user is None:
        context['name'] = ''
        return context
    if user.is_authenticated:
        profile = Profile.objects.get(user=user)
        name = profile.user_name
        context['name'] = name if name is not None else ''
        return context


class ArticleListView(generic.ListView):
    """記事の一覧を表示するview"""
    model = Article
    template_name = 'blogs/index.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーのフルネーム
        _set_full_name(context, self.request.user)

        # 公開記事のみ表示
        public_articles = Article.objects.filter(is_public=True)
        context['articles'] = public_articles
        return context


class ArticleCreateView(LoginRequiredMixin, generic.CreateView):
    """記事を追加するview"""
    model = Article
    form_class = ArticleForm
    template_name = 'blogs/article_create.html'

    def form_valid(self, form):
        """記事とユーザーを紐付ける"""
        if self.request.user.is_authenticated:
            # ACCEPT_TAGSに登録していないタグをエスケープ
            escaped_text = escape_markdown(form.instance.text, ACCEPT_TAGS)
            form.instance.text = escaped_text
            form.instance.author = self.request.user
        return super(generic.CreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーのフルネーム
        _set_full_name(context, self.request.user)
        return context


class ArticleDetailView(generic.DetailView):
    """記事の詳細を表示するview"""
    model = Article
    context_object_name = 'article'
    template_name = 'blogs/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーのフルネーム
        _set_full_name(context, self.request.user)

        # ログインユーザ
        context['login_user'] = self.request.user
        return context


class ArticleEditView(LoginRequiredMixin, generic.UpdateView):
    """記事編集画面を表示する"""
    model = Article
    form_class = ArticleForm
    template_name = 'blogs/article_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ユーザーのフルネーム
        _set_full_name(context, self.request.user)
        return context

    def form_valid(self, form):
        """記事のエスケープ処理"""
        if self.request.user.is_authenticated:
            # ACCEPT_TAGSに登録していないタグをエスケープ
            escaped_text = escape_markdown(form.instance.text, ACCEPT_TAGS)
            form.instance.text = escaped_text
        return super(generic.UpdateView, self).form_valid(form)
