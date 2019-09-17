import io
import sys

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.views import generic
from PIL import Image

from blogs.escape import escape_markdown
from blogs.forms import ArticleForm
from blogs.models import Article, Category
from users.models import Profile


ACCEPT_TAGS = [
    'b', 'blockquote', 'code', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'ol', 'ol start="42"', 'p', 'pre', 'sub', 'sup', 'strong',
    'strike', 'ul', 'br', 'hr',
]


def _image_resize(image, size):
    """画像を指定のサイズにリサイズする関数"""
    # 画像のフォーマットを取得
    im_format = 'png'
    if '.' in image.name:
        im_format = image.name.split('.')[1]

    im = Image.open(image)
    im = im.resize(size, Image.LANCZOS)

    output_file = io.BytesIO()
    if im_format == 'png':
        im.save(output_file, format='PNG')
    else:
        im.save(output_file, format='JPEG')
    output_file.seek(0)

    return InMemoryUploadedFile(
        output_file,
        'ImageField',
        image.name,
        'image/%s' % im_format,
        sys.getsizeof(output_file),
        None
    )


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
        articles = Article.objects.filter(is_public=True)
        ordered_articles = articles.order_by('-created_at')
        # カテゴリーでフィルターをかける場合
        if 'category' in self.request.GET:
            try:
                category = Category.objects.get(
                    name=self.request.GET['category']
                )
            # カテゴリーがDBに存在しなかったら空リストを返す
            except Category.DoesNotExist:
                return []
            ordered_articles = ordered_articles.filter(categories=category)
        return ordered_articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)
        # カテゴリー
        categories = Category.objects.all()
        category_counts = (
            Article.objects.filter(categories=category, is_public=True).count()
            for category in categories
        )
        category_dict = {}
        for category, category_count in zip(categories, category_counts):
            category_dict.setdefault(category, category_count)
        context['category_dict'] = category_dict
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
        # 画像処理後、親クラスのform_validを呼び出す
        return self._image_proc(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)
        return context

    def _image_proc(self, form):
        # formにデータがない場合
        if form.cleaned_data['thumbnail'] is None:
            return super(generic.CreateView, self).form_valid(form)

        # 画像のリサイズ
        form.instance.thumbnail = _image_resize(
            image=form.instance.thumbnail,
            size=(150, 150)
        )

        return super(generic.CreateView, self).form_valid(form)


class ArticleDetailView(generic.DetailView):
    """記事の詳細を表示するview"""
    model = Article
    context_object_name = 'article'
    template_name = 'blogs/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ナブバー設定用ユーザーのフルネーム
        _set_full_name(context, self.request.user)

        # 投稿者のプロフィール情報
        author_profile = Profile.objects.get(user=kwargs['object'].author)
        context['author_profile'] = author_profile

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
        # 画像処理後、親クラスのform_validを呼び出す
        return self._image_proc(form)

    def _image_proc(self, form):
        # formに画像がない場合そのまま親に渡す
        if form.cleaned_data['thumbnail'] is None:
            return super(generic.UpdateView, self).form_valid(form)

        # クリアなら画像削除後そのまま親に渡す
        article_pk = form.instance.pk
        if 'thumbnail-clear' in form.data:
            if form.data['thumbnail-clear'] == 'on':
                self._del_image(article_pk)
                return super(generic.UpdateView, self).form_valid(form)

        # 画像のリサイズ
        form.instance.thumbnail = _image_resize(
            image=form.instance.thumbnail,
            size=(150, 150)
        )
        # 更新前の画像を削除
        self._del_image(article_pk)

        return super(generic.UpdateView, self).form_valid(form)

    def _del_image(self, article_pk):
        """画像を削除"""
        article = Article.objects.get(pk=article_pk)
        if article.thumbnail:
            article.thumbnail.delete()
            article.save()


class ArticleDeleteView(LoginRequiredMixin, generic.DeleteView):
    """記事削除画面を表示"""
    model = Article
    template_name = 'blogs/article_delete.html'

    def get_success_url(self):
        profile = Profile.objects.get(user=self.request.user)
        return reverse('users:profile', kwargs={'name': profile.user_name})

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

        # 記事のタイトル
        context['article_title'] = kwargs['object'].title
        return context
