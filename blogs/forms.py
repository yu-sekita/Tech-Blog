from django import forms
from markdownx.widgets import MarkdownxWidget

from blogs.models import Article


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ('title', 'text')
        widgets = {
            'text': MarkdownxWidget(attrs={'class': 'textarea'}),
        }
