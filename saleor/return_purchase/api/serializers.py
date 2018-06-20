# site settings rest api serializers
from decimal import Decimal
import datetime
from django.utils.formats import localize
from rest_framework import serializers
from saleor.return_purchase.models import ReturnPurchase as Table
from saleor.return_purchase.models import Item
from saleor.product.models import Stock
from saleor.sale.models import Sales
from saleor.purchase.models import PurchasedItem, PurchaseVariant
from saleor.countertransfer.models import CounterTransferItems as CounterItem
from saleor.menutransfer.models import TransferItems as MenuItem

global fields, item_fields, module
module = 'return_purchase'
fields = ('id',
          'user',
          'purchase',
          'created',
          'date',
          'invoice_number')

item_fields = ('id',
               'return_purchase',
               'sku',
               'quantity',
               'product_name',
               'total_cost',
               'unit_cost',)


class ItemsSerializer(serializers.ModelSerializer):
    max_quantity = serializers.SerializerMethodField()
    returned_quantity = serializers.SerializerMethodField()
    sold_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = item_fields + ('max_quantity', 'returned_quantity', 'sold_quantity')

    def get_max_quantity(self, obj):
        # return obj.purchase_item.returnable_quantity() \
        #     if obj.purchase_item.returnable_quantity() < \
        #        obj.purchase_item.get_quantity() \
        #     else obj.purchase_item.get_quantity()
        try:
            return obj.purchase_item.stock.quantity
        except:
            return 0

    def get_returned_quantity(self, obj):
        return obj.purchase_item.returned_quantity

    def get_sold_quantity(self, obj):
        return obj.purchase_item.quantity


def format_fields(fields_data, items_list):
    """
    Exclude supplied list of fields from global item list
    :param items_list: list type of fields to exclude
    :return:
    """
    # convert tuple to list
    temp = list(fields_data)
    # remove supplied fields
    for item in items_list:
        try:
            temp.remove(str(item))
        except:
            pass
    return tuple(temp)


class ItemsStockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = item_fields


class CloseTransferItemSerializer(serializers.ModelSerializer):
    close_details = serializers.JSONField(write_only=True)

    class Meta:
        model = Item
        fields = item_fields + ('close_details',)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.closed = True
        instance.qty = validated_data.get('qty', instance.qty)
        instance.deficit = validated_data.get('deficit', instance.deficit)
        # check if close json sent then close mark it as closed
        close_details = validated_data.pop('close_details')
        try:
            if close_details['store']:
                # return to stock
                if instance.qty > 0:
                    Stock.objects.increase_stock(instance.stock, instance.qty)
                    instance.price = Decimal(instance.sold * instance.unit_price)
                    instance.qty = 0
            else:
                # transfer to tomorrows stock
                tomorrow = datetime.timedelta(days=1) + datetime.date.today()
                counter = instance.counter
                query = Table.objects. \
                    filter(counter=instance.counter, date__icontains=tomorrow)
                if not query.exists():
                    new_transfer = Table.objects.create(date=tomorrow, counter=counter)
                else:
                    new_transfer = query.first()
                carry_items(new_transfer, [instance])

        except:
            pass
        instance.save()
        return instance


def update_return(instance, quantity):
    diff = int(quantity) - int(instance.quantity)
    purchase_item = instance.purchase_item
    purchase_item.returned_quantity += diff
    purchase_item.save()
    try:
        stock = instance.purchase_item.stock
    except Exception as e:
        stock = None
    if not stock:
        stock = Stock()
        stock.variant = instance.purchase_item.variant
        stock.price_override = instance.purchase_item.price_override
        stock.quantity = 0
        stock.low_stock_threshold = instance.purchase_item.low_stock_threshold
        stock.wholesale_override = instance.purchase_item.wholesale_override
        stock.minimum_price = instance.purchase_item.minimum_price
        stock.cost_price = instance.purchase_item.unit_cost
        stock.save()
    Stock.objects.decrease_stock(stock, diff)


class UpdateItemSerializer(serializers.ModelSerializer):
    close_details = serializers.JSONField(write_only=True)

    class Meta:
        model = Item
        fields = ('id', 'quantity', 'close_details',)

    def update(self, instance, validated_data):
        """
        Update returned quantity value
        case 1: Increase quantity of returned item =>
        ---------------------------------------------
              increase purchase item returned quantity value
              reduce order quantity
              reduce stock quantity value
        case 2: reduce quantity of returned item
        ---------------------------------------------
              reduce purchased item returned quantity
              increase stock of returned quantity
        :param instance:
        :param validated_data:
        :return:
        """
        update_return(instance, validated_data.get('quantity'))

        instance.quantity = validated_data.get('quantity', instance.quantity)

        instance.save()
        return instance


class TableListSerializer(serializers.ModelSerializer):
    return_purchase_items = ItemsSerializer(many=True)
    quantity = serializers.SerializerMethodField()
    update_url = serializers.HyperlinkedIdentityField(view_name=module + ':api-update')
    update_items_url = serializers.HyperlinkedIdentityField(view_name=module + ':update')
    view_url = serializers.HyperlinkedIdentityField(view_name=module + ':update-view')

    class Meta:
        model = Table
        fields = fields + ('return_purchase_items', 'quantity', 'view_url', 'update_items_url', 'update_url')

    def get_quantity(self, obj):
        return obj.total_quantity()


def carry_items(instance, items):
    """
    Create new or update existing transferred stock items
    :param instance: model instance: Transfer instance
    :param items: dictionary: Stock item transferred
    :return:
    """
    for item in items:
        # if item exist, increase quantity else create
        try:
            item.stock = Stock.objects.get(pk=item.stock.pk)
        except Exception as e:
            pass
        query = Item.objects.filter(transfer=instance, stock=item.stock)
        if query.exists():
            single = query.first()
            single.qty = int(single.qty) + int(item.qty)
            single.transferred_qty = int(single.transferred_qty) + int(item.qty)
            single.expected_qty = single.qty
            single.price = Decimal(single.price) + Decimal(item.price)
            if single.qty > 0:
                single.save()
        else:
            single = Item()
            single.transfer = instance
            single.counter = instance.counter
            single.price = item.price
            single.unit_price = item.unit_price
            single.discount = item.discount
            single.tax = item.tax
            single.product_category = item.product_category
            single.productName = item.productName
            single.stock = item.stock
            single.qty = item.qty
            single.transferred_qty = single.qty
            single.expected_qty = single.qty
            single.sku = item.sku
            if single.qty > 0:
                single.save()

        # decrease stock
        # Stock.objects.decrease_stock(item['stock'], item['qty'])


def back_to_stock(item):
    # mark as returned
    purchase_item = PurchasedItem.objects.get(id=item.get('id')) if item.get('id') else False
    PurchasedItem.objects.add_returned_item(purchase_item, item.get('qty'))

    # reduce stock quantity
    Stock.objects.decrease_stock(purchase_item.stock, item.get('qty'))

    return {'purchase_item': purchase_item}


def create_items(instance, items):
    """
    Create new or update existing transferred stock items
    :param instance: model instance: Transfer instance
    :param items: dictionary: Stock item transferred
    :return:
    """
    for item in items:
        # return item to respective stock
        stock_details = back_to_stock(item)
        query = Item.objects.filter(return_purchase=instance, purchase_item=stock_details.get('purchase_item'))
        if query.exists():
            single = query.first()
            single.quantity = int(single.quantity) + int(item['qty'])
            single.total_cost = Decimal(single.total_cost) + Decimal(item['total_cost'])
            if single.quantity > 0:
                single.save()
        else:
            single = Item()
            single.purchase_item = stock_details.get('purchase_item')
            single.return_purchase = instance
            single.total_cost = item.get('total_cost')
            single.unit_cost = item.get('unit_cost')
            single.product_name = item.get('product_name')
            single.sku = item.get('sku')
            single.quantity = item.get('qty')
            if single.quantity > 0:
                single.save()


class CreateListSerializer(serializers.ModelSerializer):
    return_purchase_items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = fields + ('return_purchase_items',)

    def create(self, validated_data):
        instance = Table()
        instance.invoice_number = validated_data.get('invoice_number')
        instance.date = validated_data.get('date')
        return_purchase_items = validated_data.pop('return_purchase_items')

        try:
            purchase = PurchaseVariant.objects.get(invoice_number=instance.invoice_number)
            instance.purchase = purchase
        except Exception as e:
            pass
        try:
            instance = Table.objects.get(invoice_number=instance.invoice_number)
        except Exception as e:
            instance.save()

        create_items(instance, return_purchase_items)

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    # items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = ('id', 'date')

    def update(self, instance, validated_data):
        # action 1: carry forward 2: return to stock
        # tomorrow = datetime.timedelta(days=1) + datetime.date.today()
        action = validated_data.get('action')
        date = validated_data.pop('date')
        items = validated_data.pop('items')
        for cart in items:
            item = Item.objects.get(pk=cart['id'])
            item.qty = cart['qty']
            item.description = cart['description']
            item.deficit = cart['deficit']
            if action == 2:
                # return to stock
                if item.qty:
                    Stock.objects.increase_stock(item.stock, item.qty)
                    item.price = Decimal(item.sold * item.unit_price)
                    item.qty = 0
            else:
                # carry forward
                # transfer to tomorrows stock
                query = Table.objects. \
                    filter(counter=instance.counter, date__icontains=date)
                if not query.exists():
                    new_transfer = Table.objects.create(date=date, counter=instance.counter)
                else:
                    new_transfer = query.first()
                carry_items(new_transfer, [item])
                item.qty = 0

            if not item.closed:
                item.closed = True
                item.save()
        instance.save()
        return instance
