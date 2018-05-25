# site settings rest api serializers
from decimal import Decimal
from django.utils.formats import localize
from rest_framework import serializers
from saleor.countertransfer.models import CounterTransfer as Table
from saleor.countertransfer.models import CounterTransferItems as Item
from saleor.product.models import Stock

global fields, item_fields, module
module = 'countertransfer'
fields = ('id',
          'name',
          'user',
          'counter',
          'created',
          'date',
          'description')

item_fields = ('id',
               'stock',
               'sku',
               'qty',
               'transferred_qty',
               'expected_qty',
               'deficit',
               'sold',
               'tax',
               'discount',
               'price',
               'unit_price',
               'quantity',
               'counter',
               'closed',
               'productName',
               'description',
               'product_category',)


class ItemsSerializer(serializers.ModelSerializer):
    sku = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = item_fields

    def get_sku(self, obj):
        try:
            return obj.stock.variant.sku
        except:
            return ''

    def get_quantity(self, obj):
        try:
            return obj.stock.quantity
        except:
            return 0


def format_fields(items_list):
    """
    Exclude supplied list of fields from global item list
    :param items_list: list type of fields to exclude
    :return:
    """
    # convert tuple to list
    temp = list(item_fields)
    # remove supplied fields
    for item in items_list:
        temp.remove(str(item))
    return tuple(temp)


class ItemsStockSerializer(serializers.ModelSerializer):
    sku = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    counter = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = format_fields(['productName', 'price', 'unit_price']) + \
                 ('total_cost', 'product_name', 'unit_cost')

    def get_sku(self, obj):
        try:
            return obj.stock.variant.sku
        except:
            return ''

    def get_product_name(self, obj):
        return obj.productName

    def get_unit_cost(self, obj):
        try:
            return obj.stock.price_override.gross
        except:
            return obj.unit_price

    def get_total_cost(self, obj):
        try:
            return obj.price
        except:
            return 0

    def get_quantity(self, obj):
        try:
            return Item.objects.instance_quantities(obj.stock, filter_type='stock', counter=obj.counter)
        except:
            return 0
            
    def get_counter(self, obj):
        try:
            return {"id":obj.counter.id, "name":obj.counter.name}
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
        # if edit qty is more than current qty reduce stock else decrease
        if int(validated_data.get('qty')) > instance.qty:
            diff = int(validated_data.get('qty')) - int(instance.qty)
            Stock.objects.decrease_stock(instance.stock, diff)
            instance.qty = validated_data.get('qty', instance.qty)
            instance.expected_qty = instance.qty
            instance.transferred_qty = int(instance.transferred_qty) + int(diff)
        elif int(validated_data.get('qty')) < instance.qty:
            diff = int(instance.qty) - int(validated_data.get('qty'))
            Stock.objects.increase_stock(instance.stock, diff)
            instance.qty = validated_data.get('qty', instance.qty)
            instance.expected_qty = instance.qty
            instance.transferred_qty = int(instance.transferred_qty) - int(diff)
        else:
            pass

        instance.save()
        return instance


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-update')
    update_items_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:update')
    closing_items_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:close-item')
    delete_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-delete')
    text = serializers.SerializerMethodField()
    counter = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    counter_transfer_items = ItemsSerializer(many=True)
    quantity = serializers.SerializerMethodField()
    worth = serializers.SerializerMethodField()
    all_item_closed = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + (
            'quantity', 'worth', 'all_item_closed', 'counter_transfer_items', 'text',
            'closing_items_url', 'update_url', 'delete_url', 'update_items_url')

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
            item['stock'] = Stock.objects.get(pk=item['stock'])
        except:
            pass
        query = Item.objects.filter(transfer=instance, stock=item['stock'])
        if query.exists():
            print 'updating....'
            single = query.first()
            single.qty = int(single.qty) + int(item['qty'])
            single.transferred_qty = int(single.transferred_qty) + int(item['qty'])
            single.expected_qty = single.qty
            print single.transferred_qty
            single.price = Decimal(single.price) + Decimal(item['price'])
            single.save()
        else:
            single = Item()
            single.transfer = instance
            single.counter = instance.counter
            single.price = item['price']
            single.unit_price = item['price_override']
            single.discount = item['discount']
            single.tax = item['tax']
            single.product_category = item['product_category']
            single.productName = item['productName']
            single.stock = item['stock']
            single.qty = item['qty']
            single.transferred_qty = single.qty
            single.expected_qty = single.qty
            single.sku = item['sku']
            single.save()

        # decrease stock
        Stock.objects.decrease_stock(item['stock'], item['qty'])


class CreateListSerializer(serializers.ModelSerializer):
    # counter_transfer_items = ItemsSerializer(many=True)
    counter_transfer_items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = fields + ('counter_transfer_items',)

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        instance.counter = validated_data.get('counter')
        instance.date = validated_data.get('date')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        counter_transfer_items = validated_data.pop('counter_transfer_items')

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
    counter_transfer_items = ItemsSerializer(many=True)

    class Meta:
        model = Table
        fields = fields + ('counter_transfer_items', )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance
