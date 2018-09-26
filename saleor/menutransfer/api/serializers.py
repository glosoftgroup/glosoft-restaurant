# site settings rest api serializers
from decimal import Decimal
import datetime
from django.utils.formats import localize
from rest_framework import serializers
from saleor.menutransfer.models import MenuTransfer as Table
from saleor.menutransfer.models import TransferItems as Item
from saleor.product.models import Stock
from saleor.menu.models import Menu

global fields, item_fields, module
# global variable
module = 'menutransfer'
fields = ('id',
          'name',
          'user',
          'counter',
          'created',
          'date',
          'description')

item_fields = ('id',
               'menu',
               'name',
               'qty',
               'transferred_qty',
               'expected_qty',
               'deficit',
               'sold',
               'price',
               'unit_price',
               'quantity',
               'counter',
               'closed',
               'description',
               'category',)


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = item_fields


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
    sku = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    kitchen = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = format_fields(item_fields, ['qty', 'productName', 'category', 'counter', 'menu', 'name', 'price', 'unit_price']) + \
                 ('total_cost', 'tax', 'discount', 'kitchen', 'unit_cost', 'product_category', 'product_name', 'sku')

    def get_sku(self, obj):
        try:
            return obj.menu.id
        except:
            return ''

    def get_product_name(self, obj):
        return obj.name

    def get_tax(self, obj):
        return 0

    def get_quantity(self, obj):
        return obj.qty

    def get_discount(self, obj):
        return 0

    def get_product_category(self, obj):
        return obj.menu.category.name

    def get_total_cost(self, obj):
        try:
            return obj.price
        except:
            return 0

    def get_unit_cost(self, obj):
        try:
            return obj.price
        except:
            return 0

    def get_kitchen(self, obj):
        try:
            return {"id": obj.counter.id, "name": obj.counter.name}
        except:
            return None


class CloseTransferItemSerializer(serializers.ModelSerializer):
    close_details = serializers.JSONField(write_only=True)

    class Meta:
        model = Item
        fields = item_fields + ('close_details',)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.closed = True
        instance.qty = validated_data.get('qty', instance.qty)
        instance.sold = validated_data.get('sold', instance.sold)
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


class UpdateTransferItemSerializer(serializers.ModelSerializer):
    close_details = serializers.JSONField(write_only=True)

    class Meta:
        model = Item
        fields = item_fields + ('close_details',)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.closed = False
        instance.price = validated_data.get('price', instance.price)
        if int(validated_data.get('qty')) > instance.qty:
            diff = int(validated_data.get('qty')) - int(instance.qty)
            instance.qty = validated_data.get('qty', instance.qty)
            instance.expected_qty = instance.qty
            instance.transferred_qty = int(instance.transferred_qty) + int(diff)
        elif int(validated_data.get('qty')) < instance.qty:
            diff = int(instance.qty) - int(validated_data.get('qty'))
            instance.qty = validated_data.get('qty', instance.qty)
            instance.expected_qty = instance.qty
            instance.transferred_qty = int(instance.transferred_qty) - int(diff)
        else:
            pass

        instance.save()
        return instance


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name=module+':api-update')
    update_items_url = serializers.HyperlinkedIdentityField(view_name=module+':update')
    closing_items_url = serializers.HyperlinkedIdentityField(view_name=module+':close-item')
    closing_items_view_url = serializers.HyperlinkedIdentityField(view_name=module+':close-item-view')
    delete_url = serializers.HyperlinkedIdentityField(view_name=module+':api-delete')
    view_url = serializers.HyperlinkedIdentityField(view_name=module+':update-view')
    text = serializers.SerializerMethodField()
    counter = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    menu_transfer_items = ItemsSerializer(many=True)
    quantity = serializers.SerializerMethodField()
    worth = serializers.SerializerMethodField()
    all_item_closed = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + (
            'quantity', 'worth', 'all_item_closed',
            'menu_transfer_items', 'text',
            'closing_items_url', 'view_url',
            'closing_items_view_url', 'update_url',
            'delete_url', 'update_items_url')

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''

    def get_all_item_closed(self, obj):
        return obj.all_items_closed()

    def get_quantity(self, obj):
        return Item.objects.instance_quantities(obj)

    def get_worth(self, obj):
        return "{:,}".format(Item.objects.instance_worth(obj))

    def get_date(self, obj):
        return localize(obj.date)

    def get_counter(self, obj):
        try:
            return {'id': obj.counter.id, 'name': obj.counter.name }
        except:
            return ''


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
            item.menu = Item.objects.get(pk=item.menu.pk)
        except Exception as e:
            print e
            pass
        query = Item.objects.filter(transfer=instance, menu=item.menu)
        if query.exists():
            print 'updating....'
            single = query.first()
            single.qty = int(single.qty) + int(item.qty)
            single.transferred_qty = int(single.transferred_qty) + int(item.qty)
            single.expected_qty = single.qty
            print single.transferred_qty
            single.price = Decimal(single.price) + Decimal(item.price)
            if single.qty < 1:
                single.save()
        else:
            single = Item()
            single.transfer = instance
            single.counter = instance.counter
            single.price = item.price
            single.name = item.name
            single.menu = item.menu
            single.qty = item.qty
            single.transferred_qty = single.qty
            single.expected_qty = single.qty
            single.category = item.category
            single.category_id = item.category_id
            if single.qty > 0:
                single.save()

        # decrease stock
        # Stock.objects.decrease_stock(item['stock'], item['qty'])


def create_items(instance, items):
    """
    Create new or update existing transferred stock items
    :param instance: model instance: Transfer instance
    :param items: dictionary: Stock item transferred
    :return:
    """
    for item in items:
        # if item exist, increase quantity else create
        try:
            item['menu'] = Menu.objects.get(pk=item.get('id'))
        except Exception as e:
            print e
            pass
        query = Item.objects.filter(transfer=instance, menu=item['menu'])
        if query.exists():
            print 'updating....'
            single = query.first()
            single.qty = int(single.qty) + int(item['qty'])
            single.transferred_qty = int(single.transferred_qty) + int(item['qty'])
            single.expected_qty = int(single.qty)
            single.closed = False
            single.price = Decimal(single.price) + Decimal(item['price'])
            if single.qty > 0:
                single.save()
        else:
            single = Item()
            single.transfer = instance
            single.counter = instance.counter
            single.price = item['price']
            single.name = item['name']
            single.menu = item['menu']
            single.qty = int(item['qty'])
            single.transferred_qty = int(single.qty)
            single.expected_qty = int(single.qty)
            single.category = item['category']['name']
            single.category_id = item['category']['id']
            if single.qty > 0:
                single.save()


class CreateListSerializer(serializers.ModelSerializer):
    # counter_transfer_items = ItemsSerializer(many=True)
    menu_transfer_items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = fields + ('menu_transfer_items',)

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        instance.counter = validated_data.get('counter')
        instance.date = validated_data.get('date')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        counter_transfer_items = validated_data.pop('menu_transfer_items')

        # check if transfer with counter/date exists
        query = Table.objects.\
            filter(counter=instance.counter, date__icontains=instance.date)
        # if true update transferred items quantity and price
        # else save new instance and add items
        if not query.exists():
            instance.save()
        else:
            instance = query.first()

        create_items(instance, counter_transfer_items)

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = ('id', 'date', 'action', 'items', )

    def update(self, instance, validated_data):
        # action 1: carry forward 2: return to stock
        # tomorrow = datetime.timedelta(days=1) + datetime.date.today()
        action = validated_data.get('action')
        date = validated_data.pop('date')
        items = validated_data.pop('items')
        for cart in items:
            item = Item.objects.get(pk=cart['id'])
            item.qty = cart.get('qty')
            item.sold = cart.get('sold')
            item.description = cart.get('description')
            item.deficit = cart.get('deficit')
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
