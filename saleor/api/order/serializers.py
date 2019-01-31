from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ValidationError,
    JSONField
)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from ...orders.models import (Orders, OrderedItem, CancelledOrder)
from ...sale.models import Terminal, PaymentOption
from decimal import Decimal
from saleor.countertransfer.models import CounterTransferItems as Item
from saleor.customer.models import Customer
from saleor.menutransfer.models import TransferItems as MenuItem
from saleor.credit.models import Credit, CreditedItem, CreditHistoryEntry
from saleor.product.models import Stock
from saleor.mpesa_transactions.models import MpesaTransactions
from saleor.visa_transactions.models import VisaTransactions
from saleor.discount.models import Sale as Discount
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()

global item_fields
item_fields = (
    'id',
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
    'cold_quantity',
    'attributes',
    'unit_purchase',
    'total_purchase',
    'discount_id',
    'discount_quantity',
    'discount_total',
    'discount_set_status'
)


class ItemSerializer(serializers.ModelSerializer):
    attributes_list = serializers.SerializerMethodField(required=False, allow_null=True)

    class Meta:
        model = OrderedItem
        fields = item_fields + ('attributes_list',)

    def get_attributes_list(self, obj):
        if obj.attributes:
            return [obj.attributes]
        return None


class ListItemSerializer(serializers.ModelSerializer):
    counter = serializers.SerializerMethodField()
    kitchen = serializers.SerializerMethodField()
    attributes_list = serializers.SerializerMethodField()
    discounts = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    transferred_qty = serializers.SerializerMethodField()

    class Meta:
        model = OrderedItem
        fields = item_fields + ('attributes_list', 'discounts','available_stock', 'transferred_qty',)

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

    def get_available_stock(self, obj):
        """ quantity """
        try:
            if obj.counter:
                transferred_item = Item.objects.get(pk=obj.transfer_id)
            elif obj.kitchen:
                transferred_item = MenuItem.objects.get(pk=obj.transfer_id)
            stock = transferred_item.qty
        except Exception as e:
            stock = obj.quantity

        return stock

    def get_transferred_qty(self, obj):
        """ quantity """
        try:
            if obj.counter:
                transferred_item = Item.objects.get(pk=obj.transfer_id)
            elif obj.kitchen:
                transferred_item = MenuItem.objects.get(pk=obj.transfer_id)
            stock = transferred_item.transferred_qty
        except Exception as e:
            stock = obj.quantity

        return stock

    def get_discounts(self, obj):
        try:
            discounts = []
            if obj.discount_id:
                all_discounts = Discount.objects.filter(pk=obj.discount_id.pk)
                for disc in all_discounts:
                    try:
                        dis = {}
                        dis['id'] = disc.id
                        dis['name'] = disc.name
                        dis['quantity'] = disc.quantity
                        dis['price'] = disc.value
                        dis['start_time'] = disc.start_time
                        dis['end_time'] = disc.end_time
                        dis['start_date'] = disc.start_date
                        dis['end_date'] = disc.end_date
                        dis['date'] = disc.date
                        dis['day'] = disc.day
                        discounts.append(dis)
                    except Exception as e:
                        logger.info('Error in appending disc to discounts: ' + str(e))
        except Exception as e:
            logger.info('Error in assigning discounts: ' + str(e))
            discounts = []

        return discounts


class ListOrderSerializer(serializers.ModelSerializer):
    ordered_items = ListItemSerializer(many=True)
    update_url = HyperlinkedIdentityField(view_name='order-api:update-order')
    delete_url = HyperlinkedIdentityField(view_name='order-api:delete-order')

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
                  'update_url',
                  'delete_url',
                  'ordered_items',
                  'customer',
                  'mobile',
                  'customer_name',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount',
                  'point'
                  )


class SearchListOrderSerializer(serializers.ModelSerializer):
    ordered_items = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    update_url = HyperlinkedIdentityField(view_name='order-api:update-order')
    ready_collect_url = HyperlinkedIdentityField(view_name='order-api:ready-collect-order')

    class Meta:
        model = Orders
        fields = ('id',
                  'user',
                  'created',
                  'invoice_number',
                  'table',
                  'room',
                  'point',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'update_url',
                  'ready_collect_url',
                  'ordered_items',
                  'customer',
                  'mobile',
                  'customer_name',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount'
                  )

    def get_created(self, obj):
        time = obj.created.time().strftime('%H:%M %p')
        return time

    def get_point(self, orders):
        try:
            return {"id": orders.point['id'], "point": orders.point['point']}
        except Exception as e:
            return None

    def get_table(self, orders):
        try:
            if orders.table:
                return orders.table.name
            elif orders.room:
                return orders.room.name
        except Exception as e:
            return "Take Away"

    def get_user(self, orders):
        try:
            if orders.user.name:
                return orders.user.name
            elif orders.user.fullname:
                return orders.user.fullname
        except Exception as e:
            return "Not Set"

    def get_ordered_items(self, orders):
        try:
            point = self.context.get('point')
            counter = self.context.get('counter')
            status = self.context.get('status')

            if counter:
                counter = int(counter)
            else:
                counter = None

            if status.lower() == "collected" or status.lower() == "not collected":
                if status.lower() == "collected":
                    collectedStatusBoolean = True
                elif status.lower() == "not collected":
                    collectedStatusBoolean = False
                items = orders.collected_items(collectedStatusBoolean, point, counter)

            elif status.lower() == "ready" or status.lower() == "not ready":
                if status.lower() == "ready":
                    readyStatusBoolean = True
                elif status.lower() == "not ready":
                    readyStatusBoolean = False
                items = orders.ready_items(readyStatusBoolean, point, counter)

            items_array = []
            for i in items:
                try:
                    counter = {"id": i.counter.id, "name": i.counter.name}
                except:
                    counter = None

                try:
                    kitchen = {"id": i.kitchen.id, "name": i.kitchen.name}
                except:
                    kitchen = None

                item = {
                    "id": i.id,
                    "counter": counter,
                    "kitchen": kitchen,
                    "sku": i.sku,
                    "transfer_id": i.transfer_id,
                    "quantity": i.quantity,
                    "unit_cost": i.unit_cost,
                    "total_cost": i.total_cost,
                    "product_name": i.product_name,
                    "product_category": i.product_category,
                    "tax": i.tax,
                    "discount": i.discount,
                    "ready": i.ready,
                    "collected": i.collected
                }
                items_array.append(item)
            return items_array
        except Exception as e:
            return None


class MenuSearchListOrderSerializer(serializers.ModelSerializer):
    ordered_items = ListItemSerializer(many=True)
    point = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    update_url = HyperlinkedIdentityField(view_name='order-api:update-order')
    ready_collect_url = HyperlinkedIdentityField(view_name='order-api:ready-collect-order')

    class Meta:
        model = Orders
        fields = ('id',
                  'user',
                  'created',
                  'invoice_number',
                  'table',
                  'room',
                  'point',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'amount_paid',
                  'update_url',
                  'ready_collect_url',
                  'ordered_items',
                  'customer',
                  'mobile',
                  'customer_name',
                  'payment_data',
                  'status',
                  'total_tax',
                  'discount_amount'
                  )

    def get_created(self, obj):
        time = obj.created.time().strftime('%H:%M %p')
        return time

    def get_point(self, orders):
        try:
            return {"id": orders.point['id'], "point": orders.point['point']}
        except Exception as e:
            return None

    def get_table(self, orders):
        try:
            if orders.table:
                return orders.table.name
            elif orders.room:
                return orders.room.name
        except Exception as e:
            return "Take Away"

    def get_user(self, orders):
        try:
            if orders.user.name:
                return orders.user.name
            elif orders.user.fullname:
                return orders.user.fullname
        except Exception as e:
            return "Not Set"


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = ItemSerializer(many=True)
    payment_data = JSONField()
    mpesaIds = JSONField(required=False, write_only=True)
    visaIds = JSONField(required=False, write_only=True)
    old_orders = JSONField()
    point = JSONField()
    waiter = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Orders
        fields = ('id',
                  'user',
                  'invoice_number',
                  'table',
                  'room',
                  'sale_point',
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
                  'old_orders',
                  'point',
                  'waiter',
                  'mpesaIds',
                  'visaIds',
                  'customer',
                  'customer_name'
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
            if total_tax > total_net:
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

    def validate_waiter(self, value):
        data = self.get_initial()
        user_id = int(data.get('waiter'))
        try:
            user = User.objects.get(pk=user_id)
            return user
        except Exception as e:
            raise ValidationError('User specified does not exist')

    def validate_customer(self, value):
        data = self.get_initial()
        customer_id = int(data.get('customer'))
        customer_name = data.get('customer_name')
        user = None
        try:
            user = Customer.objects.get(pk=customer_id)
        except Exception as e:
            if customer_name:
                user = Customer.objects.create(name=customer_name, creditable=True)
        return user

    def create(self, validated_data):
        try:
            total_net = Decimal(validated_data.get('total_net'))
        except:
            total_net = Decimal(0)
        try:
            total_tax = Decimal(validated_data.get('total_tax'))
        except Exception as e:
            total_tax = Decimal(0)

        order = Orders()

        try:
            ordered_items_data = validated_data.pop('ordered_items')
        except Exception as e:
            raise ValidationError('Ordered items field should not be empty')
        status = validated_data.get('status')
        # make a sale
        order.user = validated_data.get('waiter')
        order.invoice_number = validated_data.get('invoice_number')
        order.total_net = validated_data.get('total_net')
        order.debt = validated_data.get('total_net')
        order.sub_total = validated_data.get('sub_total')
        order.balance = validated_data.get('balance')
        order.terminal = validated_data.get('terminal')
        if validated_data.get('table'):
            order.carry = 'Sitting'
            order.table = validated_data.get('table')
        else:
            order.carry = 'Take away'
        order.room = validated_data.get('room')
        order.amount_paid = validated_data.get('amount_paid')
        order.status = status
        order.payment_data = validated_data.get('payment_data')
        order.total_tax = total_tax
        order.mobile = validated_data.get('mobile')
        order.discount_amount = validated_data.get('discount_amount')
        order.point = validated_data.get('point')
        if validated_data.get('customer'):
            order.customer = validated_data.get('customer')
        if validated_data.get('customer_name'):
            order.customer_name = validated_data.get('customer_name')

        order.save()
        # change the status of mpesaIds so as not to picked up again
        if validated_data.get('mpesaIds'):
            change_mpesa_id_status(validated_data.get('mpesaIds'))

        if validated_data.get('visaIds'):
            change_visa_id_status(validated_data.get('visaIds'))

        # add payment options
        if validated_data.get('old_orders'):
            for i in validated_data.get('old_orders'):
                old_order = Orders.objects.get(invoice_number=i)
                old_order.status = "merged to " + str(order.invoice_number)
                old_order.delete()

        for ordered_item_data in ordered_items_data:

            OrderedItem.objects.create(orders=order, **ordered_item_data)
            if ordered_item_data.get('counter'):
                try:
                    item = Item.objects.get(pk=ordered_item_data['transfer_id'])
                    if item:
                        Item.objects.decrease_stock(item, ordered_item_data['quantity'])
                    else:
                        logger.info('stock not found')
                except Exception as e:
                    logger.error("Error reducing stock!", exception=e)
            elif ordered_item_data.get('kitchen'):
                try:
                    item = MenuItem.objects.get(pk=ordered_item_data['transfer_id'])
                    if item:
                        MenuItem.objects.decrease_stock(item, ordered_item_data['quantity'])
                    else:
                        logger.info('stock not found')
                except Exception as e:
                    logger.error('Error reducing stock!', exception=e)
            else:
                logger.info('Unknown ordered item')
        self.order = order
        return self.order


class OrderUpdateSerializer(serializers.ModelSerializer):
    ordered_items = ItemSerializer(many=True)
    payment_data = JSONField()
    mpesaIds = JSONField(required=False, write_only=True)
    visaIds = JSONField(required=False, write_only=True)
    create_credit = serializers.BooleanField(write_only=True)
    update_credit = serializers.BooleanField(write_only=True)
    due_date = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Orders
        fields = ('id',
                  'invoice_number',
                  'total_net',
                  'sub_total',
                  'balance',
                  'terminal',
                  'table',
                  'room',
                  'amount_paid',
                  'status',
                  'total_tax',
                  'discount_amount',
                  'debt',
                  'ordered_items',
                  'payment_data',
                  'mpesaIds',
                  'visaIds',
                  'customer',
                  'customer_name',
                  'create_credit',
                  'update_credit',
                  'due_date'
                  )

    def validate_status(self, value):
        data = self.get_initial()
        status = str(data.get('status'))
        if status == 'fully-paid' or status == 'payment-pending':
            status = status
            amount_paid = Decimal(data.get('amount_paid'))
            sale = Orders.objects.get(invoice_number=str(data.get('invoice_number')))
            if status == 'fully-paid' and sale.balance > amount_paid:
                raise ValidationError("Status error. Amount paid is less than balance.")
            else:
                return value
        elif status == "cancelled" or status == "credited":
            pass
            return value
        else:
            raise ValidationError('Enter correct Status. Expecting either fully-paid/payment-pending or cancelled')

    def validate_payment_data(self, value):
        data = self.get_initial()
        dictionary_value = dict(data.get('payment_data'))
        return value

    def validate_total_net(self, value):
        data = self.get_initial()
        try:
            Decimal(data.get('total_net'))
            return value
        except Exception as e:
            raise ValidationError('Total Net should be a decimal/integer')

    def validate_debt(self, value):
        data = self.get_initial()
        try:
            Decimal(data.get('debt'))
        except Exception as e:
            raise ValidationError('Debt should be a decimal/integer')
        return value

    def validate_amount_paid(self, value):
        data = self.get_initial()
        try:
            Decimal(data.get('amount_paid'))
        except Exception as e:
            raise ValidationError('Amount paid should be a decimal/integer')
        return value

    def validate_terminal(self, value):
        data = self.get_initial()
        terminal = Terminal.objects.filter(pk=int(data.get('terminal')))
        if terminal.exists():
            return value
        else:
            raise ValidationError('Terminal specified does not exist')

    def validate_customer(self, value):
        data = self.get_initial()
        customer_id = int(data.get('customer'))
        customer_name = data.get('customer_name')
        user = None
        try:
            user = Customer.objects.get(pk=customer_id)
        except Exception as e:
            if customer_name:
                user = Customer.objects.create(name=customer_name, creditable=True)
        return user

    def send_to_credit(self, order):
        credit = Credit()
        credit.user = order.user
        credit.invoice_number = order.invoice_number
        credit.total_net = order.total_net
        credit.sub_total = order.sub_total
        credit.balance = order.balance
        credit.terminal = order.terminal
        credit.amount_paid = order.amount_paid
        credit.status = order.status
        credit.status = 'payment-pending'
        credit.payment_data = order.payment_data
        credit.customer = order.customer
        credit.customer_name = order.customer_name

        try:
            if order.due_date:
                from datetime import datetime
                due_date = datetime.strptime(order.due_date, '%Y-%m-%d').date()
                credit.due_date = due_date
        except Exception as e:
            logger.error(e)

        try:
            credit.table = order.table
            credit.room = order.room
            credit.carry = 'Sitting'
        except Exception as e:
            credit.carry = 'Take Away'
            logger.error(e)
        credit.total_tax = order.total_tax
        credit.save()

        # add credit history
        try:
            history = CreditHistoryEntry()
            history.credit = credit
            history.balance = credit.total_net
            history.amount = credit.amount_paid
            history.save()
        except Exception as e:
            logger.error(e)

        for option in order.payment_data:
            try:
                pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
                credit.payment_options.add(pay_opt)
            except Exception as e:
                logger.error("error adding options " + str(e))

        for item in order.items():
            try:
                new_item = CreditedItem.objects.create(
                    credit=credit,
                    sku=item.sku,
                    quantity=item.quantity,
                    product_name=item.product_name,
                    total_cost=item.total_cost,
                    unit_cost=item.unit_cost,
                    product_category=item.product_category
                )
                new_item.counter = item.counter
                new_item.transfer_id = item.transfer_id
                new_item.order = item.id
                new_item.attributes = item.attributes
                new_item.unit_purchase = item.unit_purchase
                new_item.total_purchase = item.total_purchase
                if item.discount_id:
                    new_item.discount_id = item.discount_id.pk
                new_item.discount_quantity = item.discount_quantity
                new_item.discount_total = item.discount_total
                new_item.discount_set_status = item.discount_set_status
                new_item.cold = item.cold
                new_item.cold_quantity = item.cold_quantity

                if item.counter:
                    try:
                        stock = Stock.objects.filter(sku=item.sku).first()
                        new_item.minimum_price = stock.minimum_price
                        new_item.wholesale_override = stock.wholesale_override
                        new_item.low_stock_threshold = stock.low_stock_threshold
                        new_item.unit_purchase = stock.cost_price
                    except Exception as e:
                        pass
                elif item.kitchen:
                    new_item.is_stock = False
                else:
                    pass
                new_item.kitchen = item.kitchen
                new_item.save()
            except Exception as e:
                logger.error(e.message, exception=e)

    def update(self, instance, validated_data):

        terminal = validated_data.get('terminal', instance.terminal.id)
        terminal.amount += Decimal(validated_data.get('amount_paid', instance.amount_paid))
        terminal.save()
        instance.table = validated_data.get('table', instance.table)
        instance.room = validated_data.get('room', instance.room)
        instance.total_net = validated_data.get('total_net', instance.total_net)
        instance.debt = instance.debt - validated_data.get('amount_paid', instance.amount_paid)
        instance.amount_paid = instance.amount_paid + validated_data.get('amount_paid', instance.amount_paid)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)

        if validated_data.get('customer_name'):
            try:
                customer = Customer.objects.get(name=instance.customer_name)
            except:
                customer = Customer.objects.create(name=instance.customer_name, creditable=True)
            instance.customer = customer

        if instance.amount_paid >= instance.total_net:
            instance.status = 'fully-paid'
            instance.payment_data = validated_data.get('payment_data')
            if validated_data.get('mpesaIds'):
                change_mpesa_id_status(validated_data.get('mpesaIds'))

            if validated_data.get('visaIds'):
                change_visa_id_status(validated_data.get('visaIds'))
        else:
            instance.status = validated_data.get('status', instance.status)

        if validated_data.get('status') == "credited":
            instance.status = "credited"
        instance.last_status_change = now()
        instance.save()
        try:
            ordered_items_data = validated_data.pop('ordered_items')
        except Exception as e:
            raise ValidationError('Ordered items field should not be empty')

        # return order sold item to transfer stock then delete them
        # Item = CounterTransferItems
        items = instance.ordered_items.all()
        for data in items:
            if data.counter:
                try:
                    item = Item.objects.get(pk=data.transfer_id)
                    if item:
                        Item.objects.increase_stock(item, int(data.quantity))
                    else:
                        logger.info('counter stock not found')
                except Exception as e:
                    logger.error('could not find the counter item', exception=e)

            elif data.kitchen:
                try:
                    item = MenuItem.objects.get(pk=data.transfer_id)
                    if item:
                        MenuItem.objects.increase_stock(item, int(data.quantity))
                    else:
                        logger.info('kitchen stock not found')
                except Exception as e:
                    logger.error('could not find the kitchen item', exception=e)
            else:
                logger.info('Unkown point')

        items.delete()

        # recreate orders
        for ordered_item_data in ordered_items_data:
            OrderedItem.objects.create(orders=instance, **ordered_item_data)
            if ordered_item_data.get('counter'):
                try:
                    item = Item.objects.get(pk=int(ordered_item_data['transfer_id']))
                    if item:
                        Item.objects.decrease_stock(item, ordered_item_data['quantity'])
                    else:
                        logger.info('stock not found')
                except Exception as e:
                    logger.error('Error reducing counter stock!', exception=e)
            elif ordered_item_data.get('kitchen'):
                try:
                    item = MenuItem.objects.get(pk=ordered_item_data['transfer_id'])
                    if item:
                        MenuItem.objects.decrease_stock(item, ordered_item_data['quantity'])
                    else:
                        logger.info('stock not found')
                except Exception as e:
                    logger.error('Error reducing kitchen stock!', exception=e)
            else:
                logger.info('Kitchen or counter were not provided')

        if validated_data.get('create_credit'):
            if validated_data.get('due_date'):
                instance.due_date = validated_data.get('due_date')
            self.send_to_credit(instance)

        return instance


class ListOrderItemSerializer(serializers.ModelSerializer):
    order_number = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()

    class Meta:
        model = OrderedItem
        fields = ('id',
                  'product_name',
                  'quantity',
                  'order_number',
                  'table',
                  'sale_point')

    def get_order_number(self, obj):
        return obj.orders.id

    def get_table(self, obj):
        try:
            return obj.orders.table.id
        except Exception as e:
            return 'Take away'


class OrderReadyOrCollectedSerializer(serializers.ModelSerializer):
    ordered_items = ItemSerializer(many=True)

    class Meta:
        model = Orders
        fields = ('id',
                  'invoice_number',
                  'ordered_items',
                  )

    def update(self, instance, validated_data):
        try:
            ordered_items_data = validated_data.pop('ordered_items')
        except Exception as e:
            raise ValidationError('Ordered items field should not be empty')

        """ get all the ordered items and update their ready or collected status' """
        for ordered_item_data in ordered_items_data:
            try:
                if ordered_item_data['counter'] is not None:
                    filtereditems = OrderedItem.objects.filter(sku=ordered_item_data['sku'],
                                                               counter=ordered_item_data['counter'])
            except (Exception, IndexError) as e:
                pass

            try:
                if ordered_item_data['kitchen'] is not None:
                    filtereditems = OrderedItem.objects.filter(sku=ordered_item_data['sku'],
                                                               kitchen=ordered_item_data['kitchen'])
            except Exception as e:
                pass

            if filtereditems:
                for i in filtereditems:
                    i.ready = ordered_item_data['ready']
                    i.collected = ordered_item_data['collected']
                    i.save()
        return instance


def change_mpesa_id_status(payments_ids):
    for id in payments_ids:
        try:
            p = MpesaTransactions.objects.get(pk=int(id))
            p.client_status = 1
            p.save()
        except Exception as e:
            logger.error("change_mpesa_payment_status", message="mpesa with id " + str(id) + "not found",
                         exception=e.message)


def change_visa_id_status(payments_ids):
    for id in payments_ids:
        try:
            p = VisaTransactions.objects.get(pk=int(id))
            p.client_status = 1
            p.save()
        except Exception as e:
            logger.error("change_visa_payment_status", message="visa with id " + str(id) + "not found",
                         exception=e.message)


class ListCancelledOrderSerializer(serializers.ModelSerializer):
    payload = JSONField()

    class Meta:
        model = CancelledOrder
        fields = ('order_id',
                  'payload',
                  'created',
                  )
