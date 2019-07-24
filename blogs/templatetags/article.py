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
