from django import template
from urllib.parse import quote

register = template.Library()

@register.filter
def url_encode(value):
    """
    A template filter to URL-encode a string.
    """
    return quote(value)