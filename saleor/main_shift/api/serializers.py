# site settings rest api serializers

from rest_framework import serializers
from saleor.main_shift.models import MainShift as Table


class TableListSerializer(serializers.ModelSerializer):

    update_url = serializers.HyperlinkedIdentityField(view_name='main_shift:api-update')
    update_view_url = serializers.HyperlinkedIdentityField(view_name='main_shift:update')
    delete_url = serializers.HyperlinkedIdentityField(view_name='main_shift:api-delete')
    opening_time = serializers.SerializerMethodField()
    closing_time = serializers.SerializerMethodField()
    start_note = serializers.SerializerMethodField()
    end_note = serializers.SerializerMethodField()
    start_balance = serializers.SerializerMethodField()
    end_balance = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ('id',
                  'opening_time',
                  'closing_time',
                  'start_note',
                  'end_note',
                  'created_at',
                  'updated_at',
                  'start_balance',
                  'end_balance',
                  'update_view_url',
                  'update_url',
                  'delete_url',
                  )

    def get_opening_timee(self, obj):
        if obj.opening_time:
            return obj.opening_time
        return "-"

    def get_closing_time(self, obj):
        if obj.closing_time:
            return obj.closing_time
        return "-"

    def get_start_note(self, obj):
        if obj.start_note:
            return obj.start_note
        return "-"

    def get_end_note(self, obj):
        if obj.end_note:
            return obj.end_note
        return "-"

    def get_start_balance(self, obj):
        if obj.start_balance:
            return obj.start_balance
        return "-"

    def get_end_balance(self, obj):
        if obj.end_balance:
            return obj.end_balance
        return "-"


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
