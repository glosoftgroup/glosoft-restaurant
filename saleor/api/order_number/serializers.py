from rest_framework import serializers


class OrderNumberSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=200)
    last_order_id = serializers.CharField(max_length=200)
