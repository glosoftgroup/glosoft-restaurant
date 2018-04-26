from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from ..salepoints.models import SalePoint


class Table(models.Model):
    name = models.CharField(
        pgettext_lazy('Table field', 'Table name'),
        max_length=52, )
    number = models.IntegerField(default=Decimal(0))
    created = models.DateTimeField(
        pgettext_lazy('Table field', 'created'),
        default=now, editable=False)
    orders = models.IntegerField(default=Decimal(0))

    class Meta:
        verbose_name = pgettext_lazy('Table model', 'Table')
        verbose_name_plural = pgettext_lazy('Tables model', 'Tables')

    def __str__(self):
        return str(self.name) + ' #' + str(self.number)

