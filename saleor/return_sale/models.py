from __future__ import unicode_literals

from decimal import Decimal
from jsonfield import JSONField
from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from saleor.counter.models import Counter
from saleor.kitchen.models import Kitchen
from saleor.sale.models import Sales


class ReturnSales(models.Model):
    created = models.DateTimeField(
        pgettext_lazy('ReturnSales field', 'created'),
        default=now, editable=False)
    date = models.DateField(pgettext_lazy('ReturnSales field', 'date'),
                            default=now)
    last_status_change = models.DateTimeField(
        pgettext_lazy('ReturnSales field', 'last status change'),
        default=now, editable=False)
    sale = models.ForeignKey(
        Sales, blank=True, null=True, related_name='returned_sale'
    )
    invoice_number = models.CharField(
        pgettext_lazy('ReturnSales field', 'invoice_number'), blank=True, null=True, max_length=36, )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='return_user',
        verbose_name=pgettext_lazy('ReturnSales field', 'user'))

    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('ReturnSale model', 'ReturnSale')
        verbose_name_plural = pgettext_lazy('ReturnSales model', 'ReturnSales')

    def __str__(self):
        return self.invoice_number

    def __unicode__(self):
        return unicode(self.invoice_number)

    def total_quantity(self):
        try:
            return self.return_items.aggregate(models.Sum('quantity'))['quantity__sum']
        except Exception as e:
            return 0


class Item(models.Model):
    return_sale = models.ForeignKey(ReturnSales, related_name='return_items', on_delete=models.CASCADE)
    order = models.IntegerField(default=Decimal(1))
    sku = models.CharField(
        pgettext_lazy('Returned Item field', 'SKU'), max_length=32)
    quantity = models.IntegerField(
        pgettext_lazy('Returned Item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('Returned Item field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('Returned Item field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('Returned Item field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    product_category = models.CharField(
        pgettext_lazy('Returned Item field', 'product_category'), max_length=128, null=True)
    discount = models.DecimalField(
        pgettext_lazy('Returned Item field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)
    tax = models.IntegerField(default=Decimal(0))
    counter = models.ForeignKey(
        Counter, related_name='return_item_counter', blank=True, null=True, default='',
        verbose_name=pgettext_lazy('Returned field', 'Counter'))
    kitchen = models.ForeignKey(
        Kitchen, related_name='return_item_kitchen', blank=True, null=True, default='',
        verbose_name=pgettext_lazy('Returned field', 'Kitchen'))

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return '%d: %s' % (self.order, self.product_name)

    def __str__(self):
        return self.product_name

