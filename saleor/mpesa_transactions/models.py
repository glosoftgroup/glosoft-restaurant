from __future__ import unicode_literals

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now


class MpesaTransactions(models.Model):
    msisdn = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'MSISDN (e.g 254708374149)'),
        blank=True, null=True, max_length=255)
    first_name = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'FirstName'),
        blank=True, null=True, max_length=255)
    middle_name = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'MiddleName'),
        blank=True, null=True, max_length=255)
    last_name = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'LastName'),
        blank=True, null=True, max_length=255)
    trans_time = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransTime (e.g 20181009075311)'),
        blank=True, null=True, max_length=255)
    trans_id = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransID (e.g MJ951H6YF7)'),
        blank=True, null=True, max_length=255, unique=True)
    trans_amount = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransAmount (e.g 100.00)'),
        blank=True, null=True, max_length=255)
    org_account_balance = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'OrgAccountBalance (e.g 518663.00)'),
        blank=True, null=True, max_length=255)
    invoice_number = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'InvoiceNumber'),
        blank=True, null=True, max_length=255)
    bill_ref_number = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'BillRefNumber e.g(account name - testapi)'),
        blank=True, null=True, max_length=255)
    third_party_transid = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'ThirdPartyTransID'),
        blank=True, null=True, max_length=255)
    business_short_code = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'BusinessShortCode (e.g 600520)'),
        blank=True, null=True, max_length=255)
    transaction_type = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransactionType (e.g Pay Bill)'),
        blank=True, null=True, max_length=255)
    status = models.IntegerField(
        pgettext_lazy('MpesaTransactionsTest field', 'IS PICKED(e.g Pay Bill)'),
        default=0)

    updated_at = models.DateTimeField(
        pgettext_lazy('MpesaTransactions field', 'updated at'),
        auto_now=True, null=True)

    created_at = models.DateTimeField(pgettext_lazy('Counter field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'mpesa_transactions'
        verbose_name = pgettext_lazy('MpesaTransactions model', 'Mpesa Transactions')
        verbose_name_plural = pgettext_lazy('MpesaTransactions model', 'Mpesa Transactions')

    def __str__(self):
        return self.trans_id


class MpesaTransactionsTest(models.Model):

    msisdn = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'MSISDN (e.g 254708374149)'),
        blank=True, null=True, max_length=255)
    first_name = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'FirstName'),
        blank=True, null=True, max_length=255)
    middle_name = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'MiddleName'),
        blank=True, null=True, max_length=255)
    last_name = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'LastName'),
        blank=True, null=True, max_length=255)
    trans_time = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransTime (e.g 20181009075311)'),
        blank=True, null=True, max_length=255)
    trans_id = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransID (e.g MJ951H6YF7)'),
        blank=True, null=True, max_length=255, unique=True)
    trans_amount = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransAmount (e.g 100.00)'),
        blank=True, null=True, max_length=255)
    org_account_balance = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'OrgAccountBalance (e.g 518663.00)'),
        blank=True, null=True, max_length=255)
    invoice_number = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'InvoiceNumber'),
        blank=True, null=True, max_length=255)
    bill_ref_number = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'BillRefNumber e.g(account name - testapi)'),
        blank=True, null=True, max_length=255)
    third_party_transid = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'ThirdPartyTransID'),
        blank=True, null=True, max_length=255)
    business_short_code = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'BusinessShortCode (e.g 600520)'),
        blank=True, null=True, max_length=255)
    transaction_type = models.CharField(
        pgettext_lazy('MpesaTransactionsTest field', 'TransactionType (e.g Pay Bill)'),
        blank=True, null=True, max_length=255)
    status = models.IntegerField(
        pgettext_lazy('MpesaTransactionsTest field', 'IS PICKED(e.g Pay Bill)'),
        default=0)

    updated_at = models.DateTimeField(
        pgettext_lazy('MpesaTransactionsTest field', 'updated at'),
        auto_now=True, null=True)

    created_at = models.DateTimeField(pgettext_lazy('Counter field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'mpesa_transactions'
        verbose_name = pgettext_lazy('MpesaTransactionsTest model', 'Mpesa Transactions')
        verbose_name_plural = pgettext_lazy('MpesaTransactionsTest model', 'Mpesa Transactions')

    def __str__(self):
        return self.trans_id
