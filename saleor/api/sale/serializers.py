from rest_framework.serializers import (
                HyperlinkedIdentityField,
                ValidationError,
                JSONField
                )
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...sale.models import (
            PaymentOption,
            Terminal,
            Sales,
            SoldItem)
from saleor.countertransfer.models import CounterTransferItems as Item
from saleor.orders.models import OrderedItem, Orders
from decimal import Decimal
from django.utils.formats import localize
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


class ItemSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = SoldItem
        fields = (
                'id',
                'transfer_id',
                'order_id',
                'is_stock',
                'returned_quantity',
                'sku',
                'quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'tax',
                'discount',
                'attributes',
                'unit_purchase',
                'total_purchase',
                'discount_id',
                'discount_quantity',
                'discount_total',
                'discount_set_status'
                 )

    def get_quantity(self, obj):
        return obj.get_quantity()


class ListSaleSerializer(serializers.ModelSerializer):
    solditems = ItemSerializer(many=True)
    update_url = HyperlinkedIdentityField(view_name='order-api:update-order')
    created = serializers.SerializerMethodField()
    payment_options = serializers.SerializerMethodField()

    class Meta:
        model = Sales
        fields = ('id',
                  'user',
                  'invoice_number',
                  'table',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'update_url',
                  'solditems',
                  'customer',
                  'mobile',
                  'customer_name',
                  'payment_data',
                  'payment_options',
                  'status',
                  'total_tax',
                  'discount_amount',
                  'created'
                  )

    def get_created(self, obj):
        return localize(obj.created)

    def get_payment_options(self, obj):
        options = []
        if obj.payment_data:
            for option in obj.payment_data:
                try:
                    pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
                    options.append({"name": pay_opt.name, "amount": option['value']})
                except Exception as e:
                    options.append({"name": option['payment_id'], "amount": option['value']})
                    logger.error("error getting payments " + str(e))

        return options


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
                    print('stock not found')
            except Exception as e:
                print('Error reducing stock!')

        return sale

class ListItemSerializer(serializers.ModelSerializer):
    counter = serializers.SerializerMethodField()
    kitchen = serializers.SerializerMethodField()
    attributes_list = serializers.SerializerMethodField()

    class Meta:
        model = OrderedItem
        fields = ('id',
                  'counter',
                  'kitchen',
                  'sku',
                  'transfer_id',
                  'quantity',
                  'unit_cost',
                  'total_cost',
                  'product_name',
                  'product_category',
                  'tax',
                  'discount',
                  'ready',
                  'collected',
                  'cold',
                  'attributes',
                  'unit_purchase',
                  'total_purchase',
                  'attributes_list',
                  )

    def get_attributes_list(self, obj):
        if obj.attributes:
            return [obj.attributes]
        return None

    def get_counter(self, obj):
        try:
            return {"id": obj.counter.id, "name": obj.counter.name}
        except:
            return None

    def get_kitchen(self, obj):
        try:
            return {"id": obj.kitchen.id, "name": obj.kitchen.name}
        except:
            return None


class ListOrderSerializer(serializers.ModelSerializer):
    ordered_items = ListItemSerializer(many=True)
    created = serializers.SerializerMethodField()

    class Meta:
        model = Orders
        fields = ('id',
                  'user',
                  'created',
                  'invoice_number',
                  'table',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'ordered_items',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount',
                  'point'
                  )

    def get_created(self, obj):
        return obj.created.strftime('%Y-%m-%d %I:%M:%S %p')


