from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from saleor.kitchen.models import Kitchen as Counter
from saleor.product.models import Stock


class TransferManager(BaseUserManager):
    def all_item_closed(self, instance):
        query = self.kitchen_transfer_items.filter(closed=False, transfer=instance)
        if query.exists():
            return False
        return True

    def instance_quantities(self, instance):
        qty = self.kitchen_transfer_items.filter(transfer=instance).aggregate(models.Sum('qty'))['qty__sum']
        return qty


class KitchenTransfer(models.Model):
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name=pgettext_lazy("KitchenTransfer field", 'counter'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='kitchen_transfer_users',
        verbose_name=pgettext_lazy('Kitchen transfer user field', 'user'))
    action = models.IntegerField(
        pgettext_lazy('KitchenTransfer field', 'action'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    name = models.CharField(
        pgettext_lazy('KitchenTransfer field', 'name'), null=True, blank=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('KitchenTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('KitchenTransfer field', 'updated at'), auto_now=True, null=True)
    date = models.DateField(pgettext_lazy('KitchenTransfer field', 'date'),
                            default=now)
    created = models.DateTimeField(pgettext_lazy('KitchenTransfer field', 'created'),
                                   default=now, editable=False)
    objects = TransferManager()

    class Meta:
        app_label = 'kitchentransfer'
        verbose_name = pgettext_lazy('KitchenTransfer model', 'KitchenTransfer')
        verbose_name_plural = pgettext_lazy('KitchenTransfers model', 'KitchenTransfers')

    def __str__(self):
        return str(self.id)

    def all_items_closed(self):
        query = self.kitchen_transfer_items.filter(closed=False)
        if query.exists():
            return False
        return True


class TransferItemManager(BaseUserManager):
    def carry_forward_quantity(self, stock):
        query = self.get_queryset().filter(stock=stock)
        query = query.filter(closed=True)
        total_qty = 0
        for item in query:
            total_qty = int(total_qty) + int(item.qty)
        return total_qty

    def decrease_stock(self, instance, quantity):
        instance.sold = models.F('sold') + quantity
        instance.qty = models.F('qty') - quantity
        instance.expected_qty = instance.qty
        instance.save(update_fields=['sold', 'qty', 'expected_qty'])

    def increase_stock(self, instance, quantity):
        instance.qty = models.F('qty') + quantity
        instance.sold = models.F('sold') - quantity
        instance.expected_qty = instance.qty
        instance.save(update_fields=['qty', 'sold', 'expected_qty'])

    def instance_quantities(self, instance, filter_type='transfer', counter=None):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        if counter:
            query = query.filter(counter=counter)
        qty = query.aggregate(models.Sum('qty'))['qty__sum']
        return qty

    def instance_worth(self, instance, filter_type='transfer'):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset().filter(stock=instance)
        total = 0
        for i in query:
            total += Decimal(i.qty) * Decimal(i.stock.cost_price.gross)
        return total


class TransferItems(models.Model):
    transfer = models.ForeignKey(
        KitchenTransfer, on_delete=models.CASCADE, related_name='kitchen_transfer_items',
        verbose_name=pgettext_lazy("KitchenTransfer field", 'counter'))
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name="kitchen_item_counter", blank=True, null=True,
                                verbose_name=pgettext_lazy("TransferItems field", 'counter'))
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True, null=True,
                              verbose_name=pgettext_lazy("TransferItems field", 'stock'))
    quantity = models.IntegerField(
        pgettext_lazy('TransferItems item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    menu_category = models.IntegerField(pgettext_lazy('KitchenTransfer field', 'menu category'),
                                        validators=[MinValueValidator(0)], default=Decimal(0))
    sku = models.CharField(max_length=60, blank=True, null=True,
                           verbose_name=pgettext_lazy('TransferItems field', 'sku'))
    product_category = models.CharField(max_length=60, blank=True, null=True,
                                        verbose_name=pgettext_lazy('TransferItems field', 'category'))
    category_name = models.CharField(max_length=60, blank=True, null=True,
                                        verbose_name=pgettext_lazy('TransferItems field', 'category name'))
    price = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                                verbose_name=pgettext_lazy('TransferItems field', 'price'))
    unit_price = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                                     verbose_name=pgettext_lazy('TransferItems field', 'unit price'))

    tax = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                              verbose_name=pgettext_lazy('TransferItems field', 'tax'))
    discount = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                                   verbose_name=pgettext_lazy('TransferItems field', 'discount'))
    qty = models.PositiveIntegerField(default=1,
                                      verbose_name=pgettext_lazy('TransferItems field', 'quantity'))
    transferred_qty = models.PositiveIntegerField(default=1,
                                                  verbose_name=pgettext_lazy('TransferItems field', 'transferred_qty'))
    deficit = models.IntegerField(default=0,
                                  verbose_name=pgettext_lazy('TransferItems field', 'deficit'))
    expected_qty = models.PositiveIntegerField(default=1,
                                               verbose_name=pgettext_lazy('CounterTransfer field', 'expected_qty'))

    sold = models.PositiveIntegerField(default=0,
                                       verbose_name=pgettext_lazy('TransferItems field', 'sold'))

    productName = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name=pgettext_lazy('TransferItems field', 'product name'))
    description = models.TextField(
        verbose_name=pgettext_lazy('TransferItems field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('CounterTransfer field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('TransferItems field', 'created'),
                                   default=now, editable=False)
    closed = models.BooleanField(default=False)
    objects = TransferItemManager()

    class Meta:
        app_label = 'kitchentransfer'
        verbose_name = pgettext_lazy('TransferItem model', 'TransferItem')
        verbose_name_plural = pgettext_lazy('TransferItems model', 'TransferItems')

    def __str__(self):
        return str(self.sku) + ' ' + str(self.qty)




