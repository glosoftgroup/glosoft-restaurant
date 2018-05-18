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

item_fields = (
                'id',
                'stock',
                'sku',
                'qty',
                'tax',
                'discount',
                'price',
                'unit_price',
                'quantity',
                'counter',
                'productName',
                'product_category',
                )


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


class UpdateTransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = item_fields

    def update(self, instance, validated_data):
        # if edit qty is more than current qty reduce stock else decrease
        if int(validated_data.get('qty')) > instance.qty:
            diff = int(validated_data.get('qty')) - int(instance.qty)
            Stock.objects.decrease_stock(instance.stock, diff)
        else:
            diff = int(instance.qty) - int(validated_data.get('qty'))
            Stock.objects.increase_stock(instance.stock, diff)

        instance.qty = validated_data.get('qty', instance.qty)
        instance.price = validated_data.get('price', instance.price)

        instance.save()
        return instance


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-delete')
    text = serializers.SerializerMethodField()
    counter = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    counter_transfer_items = ItemsSerializer(many=True)
    quantity = serializers.SerializerMethodField()
    worth = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + ('quantity', 'worth', 'counter_transfer_items', 'text', 'update_url', 'delete_url',)

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''

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
            single = query.first()
            single.qty = int(single.qty) + int(item['qty'])
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
    class Meta:
        model = Table
        fields = fields

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance
