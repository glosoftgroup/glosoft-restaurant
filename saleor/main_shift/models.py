from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now


class MainShift(models.Model):
    opening_time = models.DateTimeField(default=now, editable=True)
    closing_time = models.DateTimeField(blank=True, null=True)
    start_note = models.TextField(blank=True, null=True)
    end_note = models.TextField(blank=True, null=True)
    start_balance = models.CharField(blank=True, null=True, max_length=255)
    end_balance = models.CharField(blank=True, null=True, max_length=255)
