# site settings rest api serializers

from rest_framework import serializers
from saleor.menu.models import Menu as Table

global fields
fields = ('id', 'name', 'description', 'category', 'quantity', 'price')


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='menu:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='menu:api-delete')
    category = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + ('update_url', 'delete_url',)

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''

    def get_category(self, obj):
        try:
            return {'id': obj.category.id, 'name': obj.category.name}
        except:
            return ''


class CreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = fields

    def create(self, validated_data):
        instance = Table.objects.create(**validated_data)
        return instance


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = fields

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance
