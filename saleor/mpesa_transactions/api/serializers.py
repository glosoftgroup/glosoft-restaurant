from rest_framework import serializers
from saleor.mpesa_transactions.models import MpesaTransactions

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
            'created_at',
            'created'
        )

    def get_created(self, obj):
        time = obj.created_at.time().strftime('%H:%M %p')
        return time