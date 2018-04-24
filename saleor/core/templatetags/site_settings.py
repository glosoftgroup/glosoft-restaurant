from django.conf import settings
from django import template
from saleor.site.models import SiteSettings

register = template.Library()


@register.filter
def site_settings(value):
    currency = eval('settings.'+str(value))
    return currency
