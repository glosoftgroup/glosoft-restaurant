from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator
from saleor.counter.models import Counter
from saleor.product.models import Stock


class CounterTransfer(models.Model):
    name = models.CharField(
        pgettext_lazy('CounterTransfer field', 'name'), unique=True, max_length=128)
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True,
                              verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    quantity = models.IntegerField(
        pgettext_lazy('Stock item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    description = models.TextField(
        verbose_name=pgettext_lazy('CounterTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('CounterTransfer field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('CounterTransfer field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'countertransfer'
        verbose_name = pgettext_lazy('CounterTransfer model', 'CounterTransfer')
        verbose_name_plural = pgettext_lazy('CounterTransfers model', 'CounterTransfers')

    def __str__(self):
        return self.name




