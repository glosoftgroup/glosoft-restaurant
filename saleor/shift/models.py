from __future__ import unicode_literals

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now

from saleor.userprofile.models import User


class Shift(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='shift_user',
        verbose_name=pgettext_lazy("Shift field", 'user'))

    created_at = models.DateTimeField(pgettext_lazy('Shift field', 'created'),
                                      default=now, editable=False)

    updated_at = models.DateTimeField(
        pgettext_lazy('Shift field', 'updated at'), auto_now=True)

    start_time = models.CharField(
        pgettext_lazy('Shift field', 'start_time'), blank=True, null=True, max_length=128)

    end_time = models.CharField(
        pgettext_lazy('Shift field', 'end_time'), blank=True, null=True, max_length=128)

    start_note = models.TextField(
        verbose_name=pgettext_lazy('Shift field', 'description'), blank=True, null=True)

    end_note = models.TextField(
        verbose_name=pgettext_lazy('Shift field', 'description'), blank=True, null=True)

    start_counter_balance = models.CharField(
        pgettext_lazy('Shift field', 'counter_balance'), blank=True, null=True, max_length=128,
        default="0.0")

    end_counter_balance = models.CharField(
        pgettext_lazy('Shift field', 'counter_balance'), blank=True, null=True, max_length=128)

    cashier_start_balance = models.CharField(
        pgettext_lazy('Shift field', 'counter_balance'), blank=True, null=True, max_length=128,
        default="0.0")

    cashier_end_balance = models.CharField(
        pgettext_lazy('Shift field', 'counter_balance'), blank=True, null=True, max_length=128)

    class Meta:
        app_label = 'shift'
        verbose_name = pgettext_lazy('Shift model', 'Shift')
        verbose_name_plural = pgettext_lazy('Shifts model', 'Shifts')

    def __str__(self):
        if self.user:
            return self.user.name
        return self.created

