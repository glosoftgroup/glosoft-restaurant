from __future__ import unicode_literals

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from saleor.userprofile.models import User


class VisaTransactions(models.Model):
    msisdn = models.CharField(
        pgettext_lazy('VisaTransactions field', 'MSISDN (e.g 254708374149)'),
        blank=True, null=True, max_length=255)
    first_name = models.CharField(
        pgettext_lazy('VisaTransactions field', 'FirstName'),
        blank=True, null=True, max_length=255)
    middle_name = models.CharField(
        pgettext_lazy('VisaTransactions field', 'MiddleName'),
        blank=True, null=True, max_length=255)
    last_name = models.CharField(
        pgettext_lazy('VisaTransactions field', 'LastName'),
        blank=True, null=True, max_length=255)
    trans_time = models.CharField(
        pgettext_lazy('VisaTransactions field', 'TransTime (e.g 20181009075311)'),
        blank=True, null=True, max_length=255)
    trans_id = models.CharField(
        pgettext_lazy('VisaTransactions field', 'TransID (e.g MJ951H6YF7)'),
        blank=True, null=True, max_length=255, unique=True)
    trans_amount = models.CharField(
        pgettext_lazy('VisaTransactions field', 'TransAmount (e.g 100.00)'),
        blank=True, null=True, max_length=255)
    org_account_balance = models.CharField(
        pgettext_lazy('VisaTransactions field', 'OrgAccountBalance (e.g 518663.00)'),
        blank=True, null=True, max_length=255)
    invoice_number = models.CharField(
        pgettext_lazy('VisaTransactions field', 'InvoiceNumber'),
        blank=True, null=True, max_length=255)
    bill_ref_number = models.CharField(
        pgettext_lazy('VisaTransactions field', 'BillRefNumber e.g(account name - testapi)'),
        blank=True, null=True, max_length=255)
    third_party_transid = models.CharField(
        pgettext_lazy('VisaTransactions field', 'ThirdPartyTransID'),
        blank=True, null=True, max_length=255)
    business_short_code = models.CharField(
        pgettext_lazy('VisaTransactions field', 'BusinessShortCode (e.g 600520)'),
        blank=True, null=True, max_length=255)
    transaction_type = models.CharField(
        pgettext_lazy('VisaTransactions field', 'TransactionType (e.g Pay Bill)'),
        blank=True, null=True, max_length=255)
    status = models.IntegerField(
        pgettext_lazy('VisaTransactions field',
                      'status( [0 - not picked], [1 - picked], [2 -inserted to db] )'),
        default=0)
    client_status = models.IntegerField(
        pgettext_lazy('VisaTransactions field',
                      'status( [0 - not picked], [1 - picked], [2 -inserted to db] )'),
        default=0)

    updated_at = models.DateTimeField(
        pgettext_lazy('VisaTransactions field', 'date of update'),
        auto_now=True, null=True)

    created_at = models.DateTimeField(pgettext_lazy('VisaTransactions field', 'date of create'),
                                      default=now, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='visa_transaction_user',
        verbose_name=pgettext_lazy("VisaTransactions field", 'user'))

    class Meta:
        app_label = 'visa_transactions'
        verbose_name = pgettext_lazy('VisaTransactions model', 'Visa Transactions')
        verbose_name_plural = pgettext_lazy('VisaTransactions model', 'Visa Transactions')

    def __str__(self):
        return self.trans_id
