from rest_framework.serializers import (
                HyperlinkedIdentityField,
                ValidationError,
                JSONField
                )
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...orders.models import (
            Orders,
            OrderedItem,
            )
from ...sale.models import (
            Terminal,
            Sales,
            SoldItem)
from ...product.models import (
            Stock,
            )
from saleor.countertransfer.models import CounterTransferItems as Item
from decimal import Decimal


User = get_user_model()


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoldItem
        fields = (
                'id',
                'sale_point',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'tax',
                'discount'
                 )


class ListSaleSerializer(serializers.ModelSerializer):
    ordered_items = ItemSerializer(many=True)
    update_url = HyperlinkedIdentityField(view_name='order-api:update-order')

    class Meta:
        model = Sales
        fields = ('id',
                  'user',
                  'invoice_number',
                  'table',
                  'sale_point',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'update_url',
                  'ordered_items',
                  'customer',
                  'mobile',
                  'customer_name',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount'
                  )


class CreateSaleSerializer(serializers.ModelSerializer):
    solditems = ItemSerializer(many=True)
    payment_data = JSONField()

    class Meta:
        model = Sales
        fields = ('id',
                  'user',
                  'invoice_number',
                  'table',
                  'sale_point',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount',
                  'solditems'
                  )

    def validate_total_net(self, value):
        data = self.get_initial()
        try:
            Decimal(data.get('total_net'))
        except Exception as e:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_total_tax(self, value):
        data = self.get_initial()
        try:
            total_net = Decimal(data.get('total_net'))
            total_tax = Decimal(data.get('total_tax'))
            if total_tax >= total_net:
                raise ValidationError('Total tax cannot be more than total net')
        except Exception as e:
            raise ValidationError('Total Net should be a decimal/integer')
        return value

    def validate_discount_amount(self, value):
        data = self.get_initial()
        try:
            discount = Decimal(data.get('discount_amount'))
        except Exception as e:
            raise ValidationError('Discount should be a decimal/integer *' + str(discount) + '*')
        return value

    def validate_status(self, value):
        data = self.get_initial()
        status = str(data.get('status'))
        if status == 'fully-paid' or status == 'payment-pending':
            return value
        else:
            raise ValidationError('Enter correct Status. Expecting either fully-paid/payment-pending')

    def validate_terminal(self, value):
        data = self.get_initial()
        terminal_id = int(data.get('terminal'))
        try:
            Terminal.objects.get(pk=terminal_id)
        except Exception as e:
            raise ValidationError('Terminal specified does not exist')
        return value

    def create(self, validated_data):
        # add sold amount to drawer
        try:
            total_net = Decimal(validated_data.get('total_net'))
        except Exception as e:
            total_net = Decimal(0)
        try:
            total_tax = Decimal(validated_data.get('total_tax'))
        except Exception as e:
            total_tax = Decimal(0)
        terminal = validated_data.get('terminal')
        terminal.amount += Decimal(total_net)
        terminal.save()

        sale = Sales()

        try:
            sold_items_data = validated_data.pop('solditems')
        except Exception as e:
            raise ValidationError('Ordered items field should not be empty')
        status = validated_data.get('status')
        # make a sale
        sale.user = validated_data.get('user')
        sale.invoice_number = validated_data.get('invoice_number')
        sale.total_net = validated_data.get('total_net')
        sale.debt = validated_data.get('total_net')
        sale.sub_total = validated_data.get('sub_total')
        sale.balance = validated_data.get('balance')
        sale.terminal = validated_data.get('terminal')
        #sale.table = validated_data.get('table')
        sale.sale_point = validated_data.get('sale_point')
        sale.amount_paid = validated_data.get('amount_paid')
        sale.status = status
        sale.payment_data = validated_data.get('payment_data')
        sale.total_tax = total_tax
        sale.mobile = validated_data.get('mobile')
        sale.discount_amount = validated_data.get('discount_amount')

        sale.save()
        # add payment options

        for sold_item_data in sold_items_data:
            SoldItem.objects.create(sales=sale, **sold_item_data)
            try:
                item = Item.objects.get(stock__sku=sold_item_data['sku'])
                if item:
                    Item.objects.decrease_stock(item, sold_item_data['quantity'])
                else:
                    print 'stock not found'
            except Exception as e:
                print 'Error reducing stock!'

        return sale
