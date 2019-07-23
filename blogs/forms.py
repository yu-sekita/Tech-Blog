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

    def __init__(self, *args, **kwargs):
        """Bootstrap4に対応させる"""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
