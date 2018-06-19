from __future__ import unicode_literals
from django.db import models
from django.utils.timezone import now


class Expenses(models.Model):
    added_on = models.DateTimeField(default=now, editable=False)
    expense_date = models.CharField(max_length=100, null=True, blank=True)
    voucher = models.CharField(max_length=100, null=True, blank=True)
    expense_type = models.CharField(max_length=100, null=True, blank=True)
    authorized_by = models.CharField(max_length=100, null=True, blank=True)
    received_by = models.CharField(max_length=100, null=True, blank=True)
    paid_to = models.CharField(max_length=100, null=True, blank=True)
    account = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)


class PersonalExpenses(models.Model):
    added_on = models.DateTimeField(default=now, editable=False)
    expense_date = models.CharField(max_length=100, null=True, blank=True)
    voucher = models.CharField(max_length=100, null=True, blank=True)
    expense_type = models.CharField(max_length=100, null=True, blank=True)
    authorized_by = models.CharField(max_length=100, null=True, blank=True)
    received_by = models.CharField(max_length=100, null=True, blank=True)
    paid_to = models.CharField(max_length=100, null=True, blank=True)
    account = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)


class ExpenseType(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)


class PettyCash(models.Model):
    created = models.DateTimeField(default=now, editable=False)
    opening = models.DecimalField(max_digits=100, decimal_places=2, null=True)
    added = models.DecimalField(max_digits=100, decimal_places=2, null=True)
    closing = models.DecimalField(max_digits=100, decimal_places=2, null=True)
