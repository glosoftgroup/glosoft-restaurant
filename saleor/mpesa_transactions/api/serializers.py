from rest_framework import serializers
from saleor.mpesa_transactions.models import MpesaTransactions
from decimal import Decimal

Table = MpesaTransactions


class TableListSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'id',
            'msisdn',
            'first_name',
            'middle_name',
            'last_name',
            'trans_time',
            'trans_id',
            'trans_amount',
            'org_account_balance',
            'invoice_number',
            'bill_ref_number',
            'third_party_transid',
            'business_short_code',
            'transaction_type',
            'status',
            'client_status',
            'created_at',
            'created'
        )

    def get_created(self, obj):
        time = obj.created_at.time().strftime('%H:%M %p')
        return time


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = (
            'id',
            'msisdn',
            'first_name',
            'middle_name',
            'last_name',
            'trans_time',
            'trans_id',
            'trans_amount',
            'org_account_balance',
            'invoice_number',
            'bill_ref_number',
            'third_party_transid',
            'business_short_code',
            'transaction_type',
            'status'
        )

    def validate_trans_amount(self, value):
        data = self.get_initial()
        try:
            Decimal(data.get('trans_amount'))
        except Exception as e:
            raise serializers.ValidationError('Amount should be a decimal/integer')
        return value

    def create(self, validated_data):
        instance = Table()

        instance.first_name = validated_data.get('first_name')
        instance.middle_name = validated_data.get('middle_name')
        instance.last_name = validated_data.get('last_name')
        instance.trans_id = validated_data.get('trans_id')
        instance.trans_amount = validated_data.get('trans_amount')
        instance.trans_time = validated_data.get('trans_time')
        instance.msisdn = validated_data.get('msisdn')

        instance.save()
        return instance


class DetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = (
            'id',
            'msisdn',
            'first_name',
            'middle_name',
            'last_name',
            'trans_time',
            'trans_id',
            'trans_amount',
            'org_account_balance',
            'invoice_number',
            'bill_ref_number',
            'third_party_transid',
            'business_short_code',
            'transaction_type',
            'status'
        )