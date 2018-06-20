from rest_framework import serializers
from rest_framework.serializers import (
                HyperlinkedIdentityField,
                JSONField
                )
from saleor.accounts.models import PettyCash, Expenses
from django.db.models import Sum


class PettyCashListSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    expenses = serializers.SerializerMethodField()
    view_url = HyperlinkedIdentityField(view_name='accounts:petty_cash_detail')

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


class PettyCashDetailSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    total_expenses = serializers.SerializerMethodField()
    expenses = serializers.JSONField()

    class Meta:
        model = PettyCash
        fields = ('id',
                  'created',
                  'opening',
                  'added',
                  'expenses',
                  'total_expenses',
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
            expenses = Expenses.objects.filter(added_on__icontains=date)
            if expenses:
                return expenses
            else:
                return {}
        except Exception as e:
            return {}

    def get_total_expenses(self, obj):
        date = obj.created.date().strftime('%Y-%m-%d')
        try:
            expenses = Expenses.objects.filter(added_on__icontains=date).aggregate(Sum('amount'))['amount__sum']
            if expenses:
                return expenses
            else:
                return 0
        except Exception as e:
            return 0


class PettyCashXSerializer(serializers.Serializer):
    opening_cash = serializers.CharField(max_length=200)
    cash_added = serializers.CharField(max_length=200)
    expenses_incurred = serializers.CharField(max_length=200)
    balance = serializers.CharField(max_length=200)
    expenses = serializers.JSONField(allow_null=True)