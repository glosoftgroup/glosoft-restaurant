from __future__ import unicode_literals

from datetime import datetime
from django.db import models


class MainShift(models.Model):
    opening_time = models.DateTimeField(default=datetime.now, editable=True)
    closing_time = models.DateTimeField(blank=True, null=True)
    start_note = models.TextField(blank=True, null=True)
    end_note = models.TextField(blank=True, null=True)
    start_balance = models.CharField(blank=True, null=True, max_length=255)
    end_balance = models.CharField(blank=True, null=True, max_length=255)
