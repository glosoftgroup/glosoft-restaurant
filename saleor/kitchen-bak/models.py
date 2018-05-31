from __future__ import unicode_literals

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now


class Kitchen(models.Model):
    name = models.CharField(
        pgettext_lazy('Kitchen field', 'name'), unique=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('Kitchen field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('Kitchen field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('Kitchen field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'kitchen'
        verbose_name = pgettext_lazy('Kitchen model', 'Section')
        verbose_name_plural = pgettext_lazy('Kitchens model', 'Kitchens')

    def __str__(self):
        return self.name




