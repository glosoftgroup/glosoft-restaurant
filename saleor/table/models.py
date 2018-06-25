from __future__ import unicode_literals

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now


class Table(models.Model):
    name = models.CharField(
        pgettext_lazy('Table field', 'name'), unique=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('Table field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('Table field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('Table field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'table'
        verbose_name = pgettext_lazy('Table model', 'Table')
        verbose_name_plural = pgettext_lazy('Table model', 'Tables')

    def __str__(self):
        return self.name




