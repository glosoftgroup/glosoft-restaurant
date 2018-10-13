# site settings rest api serializers

from rest_framework import serializers
from saleor.mpesa_transactions.models import MpesaTransactions, MpesaTransactionsTest

Table = MpesaTransactionsTest


class TableListSerializer(serializers.ModelSerializer):

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


class CreateListSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        instance = Table()
        instance.msisdn = validated_data.get('msisdn')
        instance.first_name = validated_data.get('first_name')
        instance.middle_name = validated_data.get('middle_name')
        instance.last_name = validated_data.get('last_name')
        instance.trans_time = validated_data.get('trans_time')
        instance.trans_id = validated_data.get('trans_id')
        instance.trans_amount = validated_data.get('trans_amount')
        instance.org_account_balance = validated_data.get('org_account_balance')
        instance.invoice_number = validated_data.get('invoice_number')
        instance.bill_ref_number = validated_data.get('bill_ref_number')
        instance.third_party_transid = validated_data.get('third_party_transid')
        instance.business_short_code = validated_data.get('business_short_code')
        instance.transaction_type = validated_data.get('transaction_type')
        instance.save()

        return instance


class UpdateSerializer(serializers.ModelSerializer):
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

    def update(self, instance, validated_data):
        instance.msisdn = validated_data.get('msisdn', instance.msisdn)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.trans_time = validated_data.get('trans_time', instance.trans_time)
        instance.trans_id = validated_data.get('trans_id', instance.trans_id)
        instance.trans_amount = validated_data.get('trans_amount', instance.trans_amount)
        instance.org_account_balance = validated_data.get('org_account_balance', instance.org_account_balance)
        instance.invoice_number = validated_data.get('invoice_number', instance.invoice_number)
        instance.bill_ref_number = validated_data.get('bill_ref_number', instance.bill_ref_number)
        instance.third_party_transid = validated_data.get('third_party_transid', instance.third_party_transid)
        instance.business_short_code = validated_data.get('business_short_code', instance.business_short_code)
        instance.transaction_type = validated_data.get('transaction_type', instance.transaction_type)
        instance.status = validated_data.get('status', instance.status)

        instance.save()

        return instance
