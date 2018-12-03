from rest_framework import serializers
from saleor.mpesa_transactions.models import MpesaTransactions
from decimal import Decimal

Table = MpesaTransactions


class TableListSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    business_short_code = serializers.SerializerMethodField()
    transaction_type = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    msisdn = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'id',
            'msisdn',
            'first_name',
            'middle_name',
            'last_name',
            'trans_time',
            'customer',
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
            'created',
            'user',
        )

    def get_created(self, obj):
        time = obj.created_at.time().strftime('%H:%M %p')
        return time

    def get_customer(self, obj):
        if obj.first_name:
            return obj.first_name + " " + obj.middle_name + " " + obj.last_name
        else:
            return "-"

    def get_business_short_code(self, obj):
        if obj.business_short_code:
            return obj.business_short_code
        else:
            return "-"

    def get_transaction_type(self, obj):
        if obj.transaction_type:
            return obj.transaction_type
        else:
            return "-"

    def get_msisdn(self, obj):
        if obj.msisdn:
            return obj.msisdn
        else:
            return "-"


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
            'status',
            'user',
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

        instance.trans_id = validated_data.get('trans_id')
        instance.trans_amount = validated_data.get('trans_amount')
        instance.msisdn = validated_data.get('msisdn')
        instance.user = validated_data.get('user')

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
            'status',
            'user',
        )