# site settings rest api serializers

from rest_framework import serializers
from saleor.countertransfer.models import CounterTransfer as Table
from saleor.countertransfer.models import CounterTransferItems as Item
from saleor.product.models import Stock

global fields, module
module = 'countertransfer'
fields = ('id',
          'name',
          'user',
          'counter',
          'created',
          'description')


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
                'id',
                'stock',
                'qty',
                'tax',
                'discount',
                'price',
                'quantity',
                'counter'
                )


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-delete')
    text = serializers.SerializerMethodField()
    counter_transfer_items = ItemsSerializer(many=True)

    class Meta:
        model = Table
        fields = fields + ('counter_transfer_items', 'text', 'update_url', 'delete_url',)

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''


class CreateListSerializer(serializers.ModelSerializer):
    # counter_transfer_items = ItemsSerializer(many=True)
    counter_transfer_items = serializers.JSONField(write_only=True)

    class Meta:
        model = Table
        fields = fields + ('counter_transfer_items',)

    def create(self, validated_data):
        Table.objects.all().delete()
        instance = Table()
        instance.name = validated_data.get('name')
        instance.counter = validated_data.get('counter')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        counter_transfer_items = validated_data.pop('counter_transfer_items')

        instance.save()

        for item in counter_transfer_items:
            try:
                item['stock'] = Stock.objects.get(pk=item['stock'])
            except:
                pass
            del item['variant']
            del item['cost_price']
            del item['price_override']

            Item.objects.create(transfer=instance, counter=instance.counter, **item)
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
