# site settings rest api serializers
from datetime import date
from decimal import Decimal
from rest_framework import serializers
from saleor.product.models import Stock as Table
from ...discount.models import Sale
from ...discount.models import get_variant_discounts

global fields, module
module = 'countertransfer'
fields = ('id',
          'variant',
          'quantity',
          'cost_price',
          'price_override')


class TableListSerializer(serializers.ModelSerializer):
    # text = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()
    price_override = serializers.SerializerMethodField()
    productName = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    discounts = serializers.SerializerMethodField()
    product_category = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = fields + ('productName', 'price', 'tax', 'discount', 'discounts',
                           'product_category', 'qty', 'stock', 'sku')

    def get_discount(self, obj):
        today = date.today()
        price = obj.price_override.gross
        discounts = Sale.objects.filter(start_date__lte=today).filter(end_date__gte=today)
        discount = 0
        discount_list = get_variant_discounts(obj.variant, discounts)
        for discount in discount_list:
            try:
                discount = discount.factor
                discount = (Decimal(discount)*Decimal(price))
            except:
                discount = discount.amount.gross

        return discount

    def get_discounts(self, obj):
        discounts = []
        today = date.today()
        all_discounts = Sale.objects.filter(start_date__lte=today).filter(end_date__gte=today)
        for discount in all_discounts:
            try:
                dis = {}
                dis['name'] = discount.name
                dis['quantity'] = discount.quantity
                dis['price'] = discount.value
                dis['start_time'] = discount.start_time
                dis['end_time'] = discount.end_time
                dis['start_date'] = discount.start_date
                dis['end_date'] = discount.end_date
                dis['date'] = discount.date
                dis['day'] = discount.day
                discounts.append(dis)
            except Exception as e:
                print(e)
                pass

        return discounts

    def get_sku(self, obj):
        return obj.variant.sku

    def get_stock(self, obj):
        try:
            return obj.id
        except:
            return 0

    def get_qty(self, obj):
        return 1

    def get_productName(self, obj):
        productName = obj.variant.display_product()
        return productName

    def get_price(self, obj):
        try:
            price = obj.price_override.gross
            return price
        except:
            return 0

    def get_tax(self, obj):
        if obj.variant.product.product_tax:
            tax = obj.variant.product.product_tax.tax
        else:
            tax = 0
        return tax

    def get_product_category(self, obj):
        product_category = obj.variant.product_category()
        return product_category

    def get_cost_price(self, obj):
        try:
            return obj.cost_price.gross
        except:
            return 0

    def get_price_override(self, obj):
        try:
            return obj.price_override.gross
        except:
            return 0

    def get_text(self, obj):
        try:
            return obj.variant.sku
        except:
            return ''


class CreateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = fields

    def create(self, validated_data):
        instance = Table()
        instance.name = validated_data.get('name')
        if validated_data.get('description'):
            instance.description = validated_data.get('description')
        instance.save()

        return instance


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = fields

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()
        return instance


class SearchTransferredStockListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sku = serializers.CharField(max_length=200)
    product_name = serializers.CharField(max_length=200, allow_null=True)
    product_category = serializers.CharField(max_length=200, allow_null=True)
    unit_cost = serializers.DecimalField(max_digits=11, decimal_places=2)
    quantity = serializers.IntegerField()
    transferred_qty = serializers.IntegerField()
    tax = serializers.CharField(max_length=200)
    discount = serializers.CharField(max_length=200)
    counter = serializers.JSONField(allow_null=True)
    kitchen = serializers.JSONField(allow_null=True)
    attributes_list = serializers.JSONField(allow_null=True)
    discounts = serializers.JSONField(allow_null=True)
