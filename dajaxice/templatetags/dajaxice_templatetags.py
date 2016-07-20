import logging

from django import template
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.html import format_html

staticfiles_storage = get_storage_class(settings.STATICFILES_STORAGE)()

register = template.Library()

log = logging.getLogger('dajaxice')


@register.simple_tag
def dajaxice_js_import():
    url = staticfiles_storage.url('dajaxice/dajaxice.core.js')
    return format_html('<script src="%s" type="text/javascript" charset="utf-8"></script>' % url)
