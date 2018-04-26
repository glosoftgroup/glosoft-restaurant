# table rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...table.models import Table
from ...orders.models import Orders
User = get_user_model()


class TableListSerializer(serializers.ModelSerializer):
    orders_url = serializers.HyperlinkedIdentityField(view_name='order-api:api-table-orders')
    new_orders = serializers.SerializerMethodField()
    fully_paid_orders = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ('id',
                  'name',
                  'orders_url',
                  'new_orders',
                  'fully_paid_orders'
                 )

    def get_new_orders(self, obj):
        return len(Orders.objects.get_table_new_orders(obj.pk))

    def get_fully_paid_orders(self, obj):
        return len(Orders.objects.get_table_orders(obj.pk))
