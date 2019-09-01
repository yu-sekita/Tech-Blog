import re

from django import forms, template


register = template.Library()


@register.filter
def is_checkbox(field):
    """チェックボックスだったらTrueを返す関数"""
    compiled = re.compile('\\<input type=\\"checkbox\\"')
    if compiled.match(str(field)):
        return True
    return False


@register.simple_tag
def get_url_replace(request, field, value):
    """GETパラメータの一部を置き換える"""
    url_dict = request.GET.copy()
    url_dict[field] = str(value)
    return url_dict.urlencode()
