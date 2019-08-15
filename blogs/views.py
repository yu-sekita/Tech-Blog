from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin
from blogs.escape import escape_markdown
from blogs.forms import ArticleForm
from django.http import HttpResponseBadRequest
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
        context['user_name'] = ''
        return context
    if user.is_authenticated:
        profile = Profile.objects.get(user=user)
        name = profile.user_name
        context['user_name'] = name if name is not None else ''
        return context


class ArticleListView(generic.ListView):
    """記事の一覧を表示するview"""
    model = Article
    context_object_name = 'articles'
    template_name = 'blogs/index.html'
    paginate_by = 12

    def get_queryset(self):
        # 公開記事のみ、作成日時の降順でソートして表示
        public_articles = Article.objects.filter(is_public=True)
        orderd_public_article = public_articles.order_by('-created_at')
        return orderd_public_article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)
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
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)
        return context


class ArticleDetailView(generic.DetailView):
    """記事の詳細を表示するview"""
    model = Article
    context_object_name = 'article'
    template_name = 'blogs/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)

        # プロフィール表示用の投稿者の名前
        profile = Profile.objects.get(user=kwargs['object'].author)
        context['create_user_name'] = profile.user_name

        # ログインユーザ
        context['login_user'] = self.request.user
        return context


class ArticleEditView(LoginRequiredMixin, generic.UpdateView):
    """記事編集画面を表示する"""
    model = Article
    form_class = ArticleForm
    template_name = 'blogs/article_edit.html'

    def get(self, request, *args, **kwargs):
        """投稿者でないユーザがgetリクエスト投げたらエラーを返す"""
        author = Article.objects.get(pk=kwargs['pk']).author
        if self.request.user == author:
            return super().get(self, request, *args, **kwargs)
        return HttpResponseBadRequest()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)
        return context

    def form_valid(self, form):
        """記事のエスケープ処理"""
        if self.request.user.is_authenticated:
            # ACCEPT_TAGSに登録していないタグをエスケープ
            escaped_text = escape_markdown(form.instance.text, ACCEPT_TAGS)
            form.instance.text = escaped_text
        return super(generic.UpdateView, self).form_valid(form)
