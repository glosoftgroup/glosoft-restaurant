from rest_framework import serializers
from saleor.accounts.models import PettyCash, Expenses
from django.db.models import Sum


class PettyCashListSerializer(serializers.Serializer):
    opening_cash = serializers.CharField(max_length=200)
    cash_added = serializers.CharField(max_length=200)
    expenses_incurred = serializers.CharField(max_length=200)
    balance = serializers.CharField(max_length=200)
    expenses = serializers.JSONField(allow_null=True)


class NewPettyCashListSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    expenses = serializers.SerializerMethodField()
    view_url = serializers.SerializerMethodField()

    class Meta:
        model = PettyCash
        fields = ('id',
                  'created',
                  'opening',
                  'added',
                  'expenses',
                  'closing',
                  'view_url',
                  )

    def get_created(self, obj):
        date = obj.created.date().strftime('%d-%m-%Y')
        time = obj.created.time().strftime('%H:%M %p')
        date_time = date+" "+time
        return date_time

    def get_expenses(self, obj):
        date = obj.created.date().strftime('%Y-%m-%d')
        try:
            expenses = Expenses.objects.filter(added_on__icontains=date).aggregate(Sum('amount'))['amount__sum']
            if expenses:
                return expenses
            else:
                return 0
        except Exception as e:
            return 0

    def get_view_url(self, obj):
        return 'No where'
