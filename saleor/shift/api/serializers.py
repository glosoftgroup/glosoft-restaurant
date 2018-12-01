# site settings rest api serializers

from rest_framework import serializers
from saleor.shift.models import Shift as Table


class TableListSerializer(serializers.ModelSerializer):
    update_url = serializers.HyperlinkedIdentityField(view_name='shift:api-update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='shift:api-delete')
    name = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    start_note = serializers.SerializerMethodField()
    end_note = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ('id',
                  'user',
                  'name',
                  'start_time',
                  'end_time',
                  'start_counter_balance',
                  'end_counter_balance',
                  'created_at',
                  'updated_at',
                  'start_note',
                  'end_note',
                  'update_url',
                  'delete_url',
                  )

    def get_name(self, obj):
        if obj.user:
            return obj.user.name
        return "-"

    def get_end_time(self, obj):
        if obj.end_time:
            return obj.end_time
        return "-"

    def get_start_note(self, obj):
        if obj.start_note:
            return obj.start_note
        return "-"

    def get_end_note(self, obj):
        if obj.end_note:
            return obj.end_note
        return "-"


class CreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id',
                  'user',
                  'start_time',
                  'start_counter_balance',
                  )

    def create(self, validated_data):
        instance = Table()
        instance.user = validated_data.get('user')
        instance.start_time = validated_data.get('start_time')
        instance.start_counter_balance = validated_data.get('start_counter_balance')
        instance.save()

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id',
                  'user',
                  'end_time',
                  'end_counter_balance',
                  )

    def update(self, instance, validated_data):
        instance.user = validated_data.get('user')
        instance.end_time = validated_data.get('end_time')
        instance.end_counter_balance = validated_data.get('end_counter_balance')

        instance.save()
        return instance
