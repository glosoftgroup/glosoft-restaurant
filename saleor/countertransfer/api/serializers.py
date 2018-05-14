# site settings rest api serializers

from rest_framework import serializers
from saleor.countertransfer.models import CounterTransfer as Table
from saleor.countertransfer.models import CounterTransferItems as Item
global fields, module
module = 'countertransfer'
fields = ('id',
          'name',
          'user',
          'created',
          'description')


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
                'order',
                'stock',
                'quantity',
                'counter'
                )


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='countertransfer:api-delete')
    text = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + ('text', 'update_url', 'delete_url',)

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''


class CreateListSerializer(serializers.ModelSerializer):
    counter_transfer_items = ItemsSerializer(many=True)

    class Meta:
        model = Table
        fields = fields + ('counter_transfer_items',)

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        counter_transfer_items = validated_data.pop('counter_transfer_items')
        print counter_transfer_items
        print '*'*120
        instance.save()

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
