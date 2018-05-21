# site settings rest api serializers

from rest_framework import serializers
from saleor.menucategory.models import MenuCategory as Table


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='menucategory:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='menucategory:api-delete')
    text = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'text',
                  'description',
                  'update_url',
                  'delete_url'
                 )

    def get_text(self, obj):
        try:
            return obj.name
        except:
            return ''


class CreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'description',
                 )

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
        fields = ('id',
                  'name',
                  'description',
                 )

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance
