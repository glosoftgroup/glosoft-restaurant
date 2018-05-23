from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.timezone import now
from django.core.validators import MinValueValidator, RegexValidator

from saleor.menucategory.models import MenuCategory as Category


class Menu(models.Model):
    name = models.CharField(
        pgettext_lazy('Menu field', 'name'), unique=True, max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 blank=True, null=True,
                                 verbose_name=pgettext_lazy("Menu field", 'counter'))

    quantity = models.IntegerField(
        pgettext_lazy('Menu field', 'quantity'),
        validators=[MinValueValidator(0)], default=Decimal(1))
    price = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal(0),
                                verbose_name=pgettext_lazy('Menu field', 'price'))
    description = models.TextField(
        verbose_name=pgettext_lazy('Menu field', 'description'), blank=True, null=True)
    updated_at = models.DateTimeField(
        pgettext_lazy('Menu field', 'updated at'), auto_now=True, null=True)
    created = models.DateTimeField(pgettext_lazy('Menu field', 'created'),
                                   default=now, editable=False)

    class Meta:
        app_label = 'menu'
        verbose_name = pgettext_lazy('Menu model', 'Menu')
        verbose_name_plural = pgettext_lazy('Menus model', 'Menus')

    def __str__(self):
        return self.name




