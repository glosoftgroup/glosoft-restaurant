from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django_prices.models import PriceField
from jsonfield import JSONField
from ..table.models import Table
from ..salepoints.models import SalePoint
from ..counter.models import Counter
from ..kitchen.models import Kitchen
from ..customer.models import Customer
from ..room.models import Room
from ..sale.models import Terminal, PaymentOption
from . import OrderStatus


class OrdersManager(models.Manager):

    def get_table_orders(self, table_pk):

        return self.get_queryset().filter(
            models.Q(table=table_pk), models.Q(status='fully-paid'))

    def get_table_new_orders(self, table_pk):

        return self.get_queryset().filter(
            models.Q(table=table_pk), models.Q(status='payment-pending'))
        
    def get_room_new_orders(self, room_pk):

        return self.get_queryset().filter(
            models.Q(room=room_pk), models.Q(status='payment-pending'))


#@python_2_unicode_compatible
class Orders(models.Model):
    status = models.CharField(
        pgettext_lazy('Orders field', 'Invoice status'),
        max_length=32, choices=OrderStatus.CHOICES, default=OrderStatus.NEW)
    created = models.DateTimeField(
        pgettext_lazy('Orders field', 'created'),
        default=now, editable=False)    
    last_status_change = models.DateTimeField(
        pgettext_lazy('Orders field', 'last status change'),
        default=now, editable=False)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, related_name='orders_customers',
        verbose_name=pgettext_lazy('Orders field', 'customer'))

    mobile = models.CharField(max_length=20, blank=True, null=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='orders_users',
        verbose_name=pgettext_lazy('Orders field', 'user'))
    language_code = models.CharField(max_length=35, default=settings.LANGUAGE_CODE)
    user_email = models.EmailField(
        pgettext_lazy('Orders field', 'user email'),
        blank=True, default='', editable=False)
    terminal = models.ForeignKey(
        Terminal, related_name='terminal_orders',blank=True, default='',
        verbose_name=pgettext_lazy('Orders field', 'terminal'))
    table = models.ForeignKey(
        Table, related_name='table_orders', blank=True, default='', null=True, on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Orders field', 'table'))
    room = models.ForeignKey(
        Room, verbose_name=pgettext_lazy('Orders field', 'rooms'),
        related_name='order_room',  blank=True, null=True,)
    sale_point = models.ForeignKey(
        SalePoint, related_name='sale_point', blank=True, default='', null=True, 
        verbose_name=pgettext_lazy('Orders field', 'Sale point'))
    invoice_number = models.CharField(
        pgettext_lazy('Orders field', 'invoice_number'), unique=True, null=True, max_length=36,)
    
    total_net = models.DecimalField(
        pgettext_lazy('Orders field', 'total net'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    sub_total = models.DecimalField(
        pgettext_lazy('Orders field', 'sub total'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    total_tax = models.DecimalField(
        pgettext_lazy('Orders field', 'total tax'), default=Decimal(0), max_digits=100, decimal_places=2)
    amount_paid = models.DecimalField(
        pgettext_lazy('Orders field', 'amount paid'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    balance = models.DecimalField(
        pgettext_lazy('Orders field', 'balance'), default=Decimal(0), max_digits=100, decimal_places=2)
    
    discount_amount = models.DecimalField(
        pgettext_lazy('Orders field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)

    discount_name = models.CharField(
        verbose_name=pgettext_lazy('Orders field', 'discount name'),
        max_length=255, default='', blank=True)
    payment_options = models.ManyToManyField(
        PaymentOption, related_name='order_payment_option', blank=True,
        verbose_name=pgettext_lazy('Sales field',
                                   'sales options'))
    payment_data = JSONField(null=True, blank=True)
    debt = models.DecimalField(
        pgettext_lazy('Order field', 'debt'), default=Decimal(0), max_digits=100, decimal_places=2)
    carry = models.CharField(
        verbose_name=pgettext_lazy('Sales field', 'carry name'),
        max_length=255, default='', blank=True)
    old_orders = JSONField(null=True, blank=True)
    point = JSONField(null=True, blank=True)
    ready = models.BooleanField(default=False)
    collected = models.BooleanField(default=False)
    objects = OrdersManager()

    class Meta:
        ordering = ('-last_status_change',)
        verbose_name = pgettext_lazy('Orders model', 'Order')
        verbose_name_plural = pgettext_lazy('Orders model', 'Orders')
        
    def __str__(self):
        return self.invoice_number

    def __unicode__(self):
        return unicode(self.invoice_number)

    def items(self):
        return self.ordered_items.all()

    def get_status(self):
        if self.status == 'fully-paid':
            return 'Complete'
        elif self.status == 'payment-pending':
            return "Pending"
        else:
            return self.status

    def ready_items(self, ready_status, point, counter_pk=None):
        if point == "counter":
            return OrderedItem.objects.filter(orders=self, ready=ready_status, counter__pk=counter_pk)
        else:
            return OrderedItem.objects.filter(orders=self, ready=ready_status, kitchen__pk=counter_pk)

    def collected_items(self, collected_status, point, counter_pk=None):
        if point == "counter":
            return OrderedItem.objects.filter(orders=self, collected=collected_status, counter__pk=counter_pk)
        else:
            return OrderedItem.objects.filter(orders=self, collected=collected_status, kitchen__pk=counter_pk)


class OrderItemManager(models.Manager):
    def reduce_quantity(self, instance, quantity):
        instance.quantity = models.F('quantity') - quantity
        instance.save(update_fields=['quantity'])


@python_2_unicode_compatible
class OrderedItem(models.Model):
    orders = models.ForeignKey(Orders, related_name='ordered_items', on_delete=models.CASCADE, null=True)
    order = models.IntegerField(default=Decimal(1))
    transfer_id = models.IntegerField(default=Decimal(0))
    sku = models.CharField(
        pgettext_lazy('OrderedItem field', 'SKU'), max_length=32)
    quantity = models.IntegerField(
        pgettext_lazy('OrderedItem field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    product_name = models.CharField(
        pgettext_lazy('OrderedItem field', 'product name'), max_length=128)
    total_cost = models.DecimalField(
        pgettext_lazy('OrderedItem field', 'total cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    unit_cost = models.DecimalField(
        pgettext_lazy('OrderedItem field', 'unit cost'), default=Decimal(0), max_digits=100, decimal_places=2)
    product_category = models.CharField(
        pgettext_lazy('OrderedItem field', 'product_category'), max_length=128, null=True)
    discount = models.DecimalField(
        pgettext_lazy('OrderedItem field', 'discount'), default=Decimal(0), max_digits=100, decimal_places=2)
    tax = models.IntegerField(default=Decimal(0))
    counter = models.ForeignKey(
        Counter, related_name='order_item_counter', blank=True, null=True, default='',
        verbose_name=pgettext_lazy('OrderedItem field', 'Counter'))
    kitchen = models.ForeignKey(
        Kitchen, related_name='order_item_kitchen', blank=True, null=True, default='',
        verbose_name=pgettext_lazy('OrderedItem field', 'Kitchen'))
    ready = models.BooleanField(default=False)
    collected = models.BooleanField(default=False)
    objects = OrderItemManager()

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return '%d: %s' % (self.order, self.product_name)

    def __str__(self):
        return self.product_name



