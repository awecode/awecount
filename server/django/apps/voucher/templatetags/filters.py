from django import template
from django.template.defaultfilters import stringfilter

from awecount.libs import commafy

register = template.Library()


@register.filter
@stringfilter
def commafies(value):
    return commafy(value)
