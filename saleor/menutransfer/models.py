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
from saleor.menu.models import Menu


class TransferManager(BaseUserManager):
    def all_item_closed(self, instance):
        query = self.menu_transfer_items.filter(closed=False, transfer=instance)
        if query.exists():
            return False
        return True

    def instance_quantities(self, instance):
        qty = self.menu_transfer_items.filter(transfer=instance).aggregate(models.Sum('qty'))['qty__sum']
        return qty

    def get_dates(self, date_from, date_to, date, mode, counter=None):
        """
        Return distinct transfer dates between dates
        :param date_from: Date: start date for date range
        :param date_to: Date: end range
        :param date: Date: filter transfer for specific date
        :param mode: string : month, year, range
        :return: a list of dates
        """
        query = self.all()
        if counter:
            query = query.filter(counter__pk=counter)
        if date:
            year = date.split("-")[0]
            if len(date.split('-')) >= 2:
                month = date.split("-")[1]
            else:
                month = "01"
            if mode == "month":
                query = query.filter(date__year=year, date__month=month)
            elif mode == "year":
                query = query.filter(date__year=year)
            else:
                query = query.filter(date__icontains=date)
        elif date_from and date_to:
            if mode:
                year_from = date_from.split("-")[0]
                if len(date_from.split('-')) >= 2:
                    month_from = date_from.split("-")[1]
                else:
                    month_from = "01"

                year_to = date_to.split("-")[0]
                if len(date_to.split('-')) >= 2:
                    month_to = date_to.split("-")[1]
                else:
                    month_to = "01"

                if mode == "month":
                    query = query.filter(date__year__gte=year_from,
                                         date__month__gte=month_from,
                                         date__year__lte=year_to,
                                         date__month__lte=month_to)
                elif mode == "year":
                    query = query.filter(date__year__gte=year_from,
                                         date__year__lte=year_to)
                else:
                    query = query.filter(date__range=[date_from, date_to])
            else:
                query = query.filter(date__range=[date_from, date_to])

        query_dates = query.values_list('date').annotate(
            total_item=models.Sum('menu_transfer_items__transferred_qty'))
        return sorted([list(d)[0] for d in query_dates])

    def recharts_items_filter(self, date_from=None, date_to=None, date=None, mode=None, counter=None):
        dates, items = self.get_dates(date_from, date_to, date, mode, counter), []
        for date in dates:
            query_date = date
            date_transfers = self.filter(date__icontains=query_date)
            transferred, sold, deficit = 0, 0, 0
            for transfer in date_transfers:
                transferred += transfer.menu_transfer_items.all().aggregate(total=models.Sum('transferred_qty'))['total']
                sold += transfer.menu_transfer_items.all().aggregate(total=models.Sum('sold'))['total']
                deficit += transfer.menu_transfer_items.all().aggregate(total=models.Sum('deficit'))['total']
            items.append({
                'name': query_date, 'sold': sold,
                'transferred': transferred, 'deficit': deficit
            })
        return items

    def generate_title(self, title, date_from, date_to, date, mode):
        if date_from and date_to:
            title = title + ' from ' + str(date_from) + ' to ' + str(date_to)
        elif date:
            title = title + str(date)
            del date
        else:
            pass
        return title

    def highcharts_pie_filter(self, date_from=None, date_to=None, date=None, mode=None, counter=None):
        dates, items = self.get_dates(date_from, date_to, date, mode, counter), []
        transferred, sold, deficit = 0, 0, 0
        for query_date in dates:
            date_transfers = self.filter(date__icontains=query_date)

            for transfer in date_transfers:
                transferred += transfer.menu_transfer_items.all().aggregate(total=models.Sum('transferred_qty'))['total']
                sold += transfer.menu_transfer_items.all().aggregate(total=models.Sum('sold'))['total']
                deficit += transfer.menu_transfer_items.all().aggregate(total=models.Sum('deficit'))['total']
        items.append({'name': 'sold', 'y': sold})
        items.append({'name': 'deficit', 'y': deficit}),
        items.append({'name': 'transferred', 'y': transferred})
        title = self.generate_title('Menu Transfer Report ', date_from, date_to, date, mode)
        data = {
            'data': items,
            'title': title,
            'name': 'Quantity'
        }
        return data

    def all_items_filter(self, start_date=None, end_date=None):
        query = self.all()
        if start_date and end_date is not None:
            query = query.filter(
                models.Q(date__gte=start_date) &
                models.Q(date__lte=end_date)
            )
        else:
            if start_date is not None:
                query = query.filter(date__gte=start_date)
            if end_date is not None:
                query = query.filter(date__lte=end_date)
        query_dates = query.values_list('date').annotate(total_item=models.Sum('kitchen_transfer_items__transferred_qty'))
        categories, transferred, sold = [], [], []
        for date in query_dates:
            # query_date = list(date)[0]
            categories.append(date)
            date_transfers = self.filter(date__icontains=date)
            for transfer in date_transfers:
                transferred.append(transfer.menu_transfer_items.all().aggregate(total=models.Sum('transferred_qty'))['total'])
                sold.append(transfer.menu_transfer_items.all().aggregate(total=models.Sum('sold'))['total'])
        data = {
            'categories': categories,
            'series': [
                {'name': 'transferred', 'data': transferred},
                {'name': 'sold', 'data': sold},
            ]
        }
        return data


class MenuTransfer(models.Model):
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name=pgettext_lazy("MenuTransfer field", 'counter'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='menu_transfer_users',
        verbose_name=pgettext_lazy('Menu transfer user field', 'user'))
    action = models.IntegerField(
        pgettext_lazy('Menu transfer field', 'action'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    name = models.CharField(
        pgettext_lazy('MenuTransfer field', 'name'), null=True, blank=True, max_length=128)
    description = models.TextField(
        verbose_name=pgettext_lazy('MenuTransfer field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('MenuTransfer field', 'updated at'), auto_now=True, null=True)
    date = models.DateField(pgettext_lazy('MenuTransfer field', 'date'),
                            default=now)
    created = models.DateTimeField(pgettext_lazy('MenuTransfer field', 'created'),
                                   default=now, editable=False)
    trashed = models.BooleanField(default=False)

    objects = TransferManager()

    class Meta:
        app_label = 'menutransfer'
        verbose_name = pgettext_lazy('MenuTransfer model', 'MenuTransfer')
        verbose_name_plural = pgettext_lazy('MenuTransfers model', 'MenuTransfers')

    def __str__(self):
        return str(self.id)

    def all_items_closed(self):
        query = self.menu_transfer_items.filter(closed=False)
        if query.exists():
            return False
        return True

    def any_closed(self):
        """ Return true if one of its transferred item is closed """
        query = self.kitchen_transfer_items.filter(closed=True)
        if query.exists():
            return True
        return False


class TransferItemManager(BaseUserManager):
    def carry_forward_quantity(self, stock):
        query = self.get_queryset() #.filter(stock=stock)
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
            query = self.get_queryset()  #.filter(stock=instance)
        if counter:
            query = query.filter(counter=counter)
        qty = query.aggregate(models.Sum('qty'))['qty__sum']
        return qty

    def instance_worth(self, instance, filter_type='transfer'):
        return 0

    def instance_sold_quantity(self, instance, filter_type='transfer', counter=None):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset()
        if counter:
            query = query.filter(counter=counter)
        qty = query.aggregate(models.Sum('sold'))['sold__sum']
        return qty

    def instance_sold_price(self, instance, filter_type='transfer'):
        if filter_type == 'transfer':
            query = self.get_queryset().filter(transfer=instance)
        else:
            query = self.get_queryset()  # filter(stock=instance)
        total = 0
        for i in query:
            total += Decimal(i.sold) * Decimal(i.price)
        return total


class TransferItems(models.Model):
    transfer = models.ForeignKey(
        MenuTransfer, on_delete=models.CASCADE, related_name='menu_transfer_items',
        verbose_name=pgettext_lazy("TransferItems field", 'counter'))
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name="menu_item_counter", blank=True, null=True,
                                verbose_name=pgettext_lazy("TransferItems field", 'counter'))
    menu = models.ForeignKey(Menu, related_name="menu_stock", on_delete=models.CASCADE,
                             blank=True, null=True,
                             verbose_name=pgettext_lazy("TransferItems field", 'stock'))
    quantity = models.IntegerField(
        pgettext_lazy('TransferItems item field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    category_id = models.IntegerField(
        pgettext_lazy('TransferItems item field', 'category id'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    name = models.CharField(max_length=60, blank=True, null=True,
                           verbose_name=pgettext_lazy('TransferItems field', 'name'))
    category = models.CharField(max_length=60, blank=True, null=True,
                                        verbose_name=pgettext_lazy('TransferItems field', 'category'))

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
    trashed = models.BooleanField(default=False)
    objects = TransferItemManager()

    class Meta:
        app_label = 'menutransfer'
        verbose_name = pgettext_lazy('TransferItem model', 'TransferItem')
        verbose_name_plural = pgettext_lazy('TransferItems model', 'TransferItems')

    def __str__(self):
        return str(self.pk) + ' ' + str(self.qty)




