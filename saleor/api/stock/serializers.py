# site settings rest api serializers

from rest_framework import serializers
from saleor.product.models import Stock as Table

global fields, module
module = 'countertransfer'
fields = ('id',
          'variant',
          'quantity',
          'cost_price',
          'price_override')


class TableListSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()
    price_override = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + ('text',)

    def get_cost_price(self, obj):
        try:
            return obj.cost_price.gross
        except:
            return 0

    def get_price_override(self, obj):
        try:
            return obj.price_override.gross
        except:
            return 0

    def get_text(self, obj):
        try:
            return obj.variant.sku
        except:
            return ''


class CreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = fields

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
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
