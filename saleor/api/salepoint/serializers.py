# table rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...salepoints.models import SalePoint
User = get_user_model()


class SalePointListSerializer(serializers.ModelSerializer):
    orders_url = serializers.HyperlinkedIdentityField(view_name='order-api:api-sale_point-orders')
    category_url = serializers.HyperlinkedIdentityField(view_name='category-api:api-sale_point-categories')
    tables_url = serializers.HyperlinkedIdentityField(view_name='table-api:api-sale_point-table')
    items_url = serializers.HyperlinkedIdentityField(view_name='order-api:api-sale_point-orders-items')

    class Meta:
        model = SalePoint
        fields = ('id',
                  'category_url',
                  'items_url',
                  'name',
                  'orders_url',
                  'tables_url',

                 )

class CountersAndKitchensSerializer(serializers.Serializer):
   id = serializers.CharField()
   name = serializers.CharField()
   point = serializers.CharField()
