from __future__ import unicode_literals

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now


class MenuCategory(models.Model):
    name = models.CharField(
        pgettext_lazy('MenuCategory field', 'name'), unique=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('MenuCategory field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('MenuCategory field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('MenuCategory field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'menucategory'
        verbose_name = pgettext_lazy('MenuCategory model', 'MenuCategory')
        verbose_name_plural = pgettext_lazy('MenuCategories model', 'MenuCategories')

    def __str__(self):
        return self.name




