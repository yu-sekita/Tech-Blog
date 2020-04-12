from django import forms
from markdownx.widgets import MarkdownxWidget

from blogs.models import Article


class ArticleForm(forms.ModelForm):
    keywords = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'seo,key,word'
    }))

    class Meta:
        model = Article
        fields = (
            'thumbnail', 'categories', 'title', 'text', 'is_public',
            'title_for_seo', 'description', 'keywords'
        )
        widgets = {
            'text': MarkdownxWidget(attrs={'class': 'textarea'}),
        }

    def __init__(self, *args, **kwargs):
        """Bootstrap4に対応させる"""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
