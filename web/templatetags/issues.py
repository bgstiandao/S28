from django.template import Library

from web import models
from django.urls import reverse     #反向生成url

register = Library()


@register.simple_tag
def string_just(num):
    if num < 100:
        num = str(num).zfill(3)

    return "#{}".format(num)