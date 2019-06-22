
from django import template
from django.utils.safestring import mark_safe
import markdown
from markdownx.settings import (
    MARKDOWNX_MARKDOWN_EXTENSIONS,
    MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS
)
from markdownx.utils import markdownify
from markdown.extensions import Extension


register = template.Library()


@register.filter
def markdown_to_html(text):
    """マークダウンをhtmlに変換する"""
    return mark_safe(markdownify(text))


class EscapeHtml(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')


@register.filter
def markdown_to_html_with_escape(text):
    """マークダウンをhtmlに変換する

    生のhtmlやJavaScriptなどをエスケープした上で、htmlに変換する

    """
    extentions = MARKDOWNX_MARKDOWN_EXTENSIONS + [EscapeHtml]
    html = markdown.markdown(
        text,
        extentions=extentions,
        extension_configs=MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS
    )
    return mark_safe(html)
