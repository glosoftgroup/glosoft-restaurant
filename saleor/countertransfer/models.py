from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from saleor.counter.models import Counter
from saleor.product.models import Stock


class TransferManager(BaseUserManager):
    def instance_quantities(self, instance):
        qty = self.counter_transfer_items.filter(transfer=instance).aggregate(models.Sum('qty'))['qty__sum']
        return qty


class CounterTransfer(models.Model):
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='counter_transfer_users',
        verbose_name=pgettext_lazy('Sales field', 'user'))
    name = models.CharField(
        pgettext_lazy('CounterTransfer field', 'name'), null=True, blank=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('CounterTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('CounterTransfer field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('CounterTransfer field', 'created'),
                                   default=now, editable=False)

    objects = TransferManager()

    class Meta:
        app_label = 'countertransfer'
        verbose_name = pgettext_lazy('CounterTransfer model', 'CounterTransfer')
        verbose_name_plural = pgettext_lazy('CounterTransfers model', 'CounterTransfers')

    def __str__(self):
        return self.id


class TransferItemManager(BaseUserManager):
    def instance_quantities(self, instance):
        qty = self.get_queryset().filter(transfer=instance)
        qty = qty.aggregate(models.Sum('qty'))['qty__sum']
        return qty

    def instance_worth(self, instance):
        query = self.get_queryset().filter(transfer=instance)
        total = 0
        for i in query:
            total += Decimal(i.qty) * i.price
        return total


class CounterTransferItems(models.Model):
    transfer = models.ForeignKey(
        CounterTransfer, on_delete=models.CASCADE, related_name='counter_transfer_items',
        verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name=pgettext_lazy("CounterTransfer field", 'counter'))
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True,
                              verbose_name=pgettext_lazy("CounterTransfer field", 'stock'))
    quantity = models.IntegerField(
        pgettext_lazy('Stock item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    sku = models.CharField(max_length=60, blank=True, null=True,
                           verbose_name=pgettext_lazy('CounterTransfer field', 'sku'))
    product_category = models.CharField(max_length=60, blank=True, null=True,
                                        verbose_name=pgettext_lazy('CounterTransfer field', 'category'))
    price = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                                verbose_name=pgettext_lazy('CounterTransfer field', 'price'))
    tax = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                              verbose_name=pgettext_lazy('CounterTransfer field', 'tax'))
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                                   verbose_name=pgettext_lazy('CounterTransfer field', 'discount'))
    qty = models.PositiveIntegerField(default=1,
                                      verbose_name=pgettext_lazy('CounterTransfer field', 'quantity'))
    productName = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name=pgettext_lazy('CounterTransfer field', 'product name'))
    description = models.TextField(
        verbose_name=pgettext_lazy('CounterTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('CounterTransfer field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('CounterTransfer field', 'created'),
                                   default=now, editable=False)
    objects = TransferItemManager()

    class Meta:
        app_label = 'countertransfer'
        verbose_name = pgettext_lazy('CounterTransfer model', 'CounterTransfer')
        verbose_name_plural = pgettext_lazy('CounterTransfers model', 'CounterTransfers')

    def __str__(self):
        return str(self.sku) + ' ' + str(self.qty)




