from rest_framework import serializers


class ShiftSerializer(serializers.Serializer):
    is_started_shift = serializers.BooleanField()
