from rest_framework import serializers


class CodeNumberSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=200)
