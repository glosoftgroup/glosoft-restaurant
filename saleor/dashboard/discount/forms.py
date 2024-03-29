import uuid

from django import forms
from django.conf import settings
from django.utils.translation import pgettext_lazy
from django_prices.forms import PriceField

from ...discount.models import Sale, Voucher
from ...shipping.models import ShippingMethodCountry, COUNTRY_CODE_CHOICES
from structlog import get_logger

logger = get_logger(__name__)


class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        exclude = []

    def __init__(self, *args, **kwargs):        
        super(SaleForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        field = self.fields['variant'] 
        field.widget.attrs['class'] = 'form-control multiselects'
        field.widget.attrs['multiple'] = 'multiple'
        field.widget.attrs['id'] = 'variants'

        field = self.fields['customers'] 
        field.widget.attrs['class'] = 'form-control multiselect'
        field.widget.attrs['multiple'] = 'multiple'

        field = self.fields['categories'] 
        field.widget.attrs['class'] = 'form-control multiselect'
        field.widget.attrs['multiple'] = 'multiple'

        CHOICES = ((None, 'None',), ('Monday', 'Monday',), ('Tuesday', 'Tuesday',), ('Wednesday', 'Wednesday',),
                   ('Thursday', 'Thursday',), ('Friday', 'Friday',), ('Saturday', 'Saturday',), ('Sunday', 'Sunday',))
        self.fields['day'] = forms.ChoiceField(choices=CHOICES, widget=forms.Select, initial='1')
        field = self.fields['day']
        field.widget.attrs['class'] = 'form-control bootstrap-select'
        field.widget.attrs['id'] = 'id_day'

        field = self.fields['date']
        field.widget.attrs['class'] = 'form-control pickadate-selectors'
        field.widget.attrs['id'] = 'id_date'

        field = self.fields['start_date']
        field.widget.attrs['class'] = 'form-control pickadate-selectors'
        field.widget.attrs['id'] = 'id_start_date'

        field = self.fields['end_date']
        field.widget.attrs['class'] = 'form-control pickadate-selectors'
        field.widget.attrs['id'] = 'id_end_date'

        field = self.fields['start_time']
        field.widget.attrs['class'] = 'form-control timepicker'
        field.widget.attrs['id'] = 'id_start_time'

        field = self.fields['end_time']
        field.widget.attrs['class'] = 'form-control timepicker'
        field.widget.attrs['id'] = 'id_end_time'

        field = self.fields['value']
        field.widget.attrs['required'] = 'required'
        field.widget.attrs['id'] = 'id_value'

        field = self.fields['quantity']
        field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['id'] = 'id_quantity'

    def clean(self):
        try:
            cleaned_data = super(SaleForm, self).clean()
            discount_type = cleaned_data['type']
            value = cleaned_data['value']
            if discount_type == Sale.PERCENTAGE and value > 100:
                self.add_error('value', pgettext_lazy(
                    'Sale (discount) error',
                    'Sale cannot exceed 100%'))
            return cleaned_data
        except Exception as e:
            logger.error(e)


class VoucherForm(forms.ModelForm):

    class Meta:
        model = Voucher
        exclude = ['limit', 'apply_to', 'product', 'category']

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance')
        if instance and instance.id is None and not initial.get('code'):
            initial['code'] = self._generate_code
        kwargs['initial'] = initial
        super(VoucherForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def _generate_code(self):
        while True:
            code = str(uuid.uuid4()).replace('-', '').upper()[:12]
            if not Voucher.objects.filter(code=code).exists():
                return code


def country_choices():
    country_codes = ShippingMethodCountry.objects.all()
    country_codes = country_codes.values_list('country_code', flat=True)
    country_codes = country_codes.distinct()
    country_dict = dict(COUNTRY_CODE_CHOICES)
    return [
        (country_code, country_dict[country_code])
        for country_code in country_codes]


class ShippingVoucherForm(forms.ModelForm):

    limit = PriceField(
        min_value=0, required=False, currency=settings.DEFAULT_CURRENCY,
        label=pgettext_lazy(
            'Shipping voucher form label for `limit` field',
            'Only if order is over or equal to'))
    apply_to = forms.ChoiceField(
        label=pgettext_lazy(
            'Shipping voucher form label for `apply_to` field',
            'Country'),
        choices=country_choices,
        required=False)

    class Meta:
        model = Voucher
        fields = ['apply_to', 'limit']

    def save(self, commit=True):
        self.instance.category = None
        self.instance.product = None
        return super(ShippingVoucherForm, self).save(commit)


class ValueVoucherForm(forms.ModelForm):

    limit = PriceField(
        min_value=0, required=False, currency=settings.DEFAULT_CURRENCY,
        label=pgettext_lazy(
            'Value voucher form label for `limit` field',
            'Only if purchase value is greater than or equal to'))

    class Meta:
        model = Voucher
        fields = ['limit']

    def save(self, commit=True):
        self.instance.category = None
        self.instance.apply_to = None
        self.instance.product = None
        return super(ValueVoucherForm, self).save(commit)


class ProductVoucherForm(forms.ModelForm):

    apply_to = forms.ChoiceField(
        choices=Voucher.APPLY_TO_PRODUCT_CHOICES, required=False)

    class Meta:
        model = Voucher
        fields = ['product', 'apply_to']

    def __init__(self, *args, **kwargs):
        super(ProductVoucherForm, self).__init__(*args, **kwargs)
        self.fields['product'].required = True

    def save(self, commit=True):
        self.instance.category = None
        self.instance.limit = None
        # Apply to one with percentage discount is more complicated case.
        # On which product we should apply it? On first, last or cheapest?
        # Percentage case is limited to the all value and the apply_to field
        # is not used in this case so we set it to None.
        if (self.instance.discount_value_type ==
                Voucher.DISCOUNT_VALUE_PERCENTAGE):
            self.instance.apply_to = None
        return super(ProductVoucherForm, self).save(commit)


class CategoryVoucherForm(forms.ModelForm):

    apply_to = forms.ChoiceField(
        choices=Voucher.APPLY_TO_PRODUCT_CHOICES, required=False)

    class Meta:
        model = Voucher
        fields = ['category', 'apply_to']

    def __init__(self, *args, **kwargs):
        super(CategoryVoucherForm, self).__init__(*args, **kwargs)
        self.fields['category'].required = True

    def save(self, commit=True):
        self.instance.limit = None
        self.instance.product = None
        # Apply to one with percentage discount is more complicated case.
        # On which product we should apply it? On first, last or cheapest?
        # Percentage case is limited to the all value and the apply_to field
        # is not used in this case so we set it to None.
        if (self.instance.discount_value_type ==
                Voucher.DISCOUNT_VALUE_PERCENTAGE):
            self.instance.apply_to = None
        return super(CategoryVoucherForm, self).save(commit)
