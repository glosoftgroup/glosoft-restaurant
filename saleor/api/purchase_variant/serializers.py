from django.utils.formats import localize
import random
from rest_framework.serializers import (
    HyperlinkedIdentityField,
    SerializerMethodField,
    ValidationError,
    JSONField
)
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...purchase.models import PurchaseVariant as Table
from saleor.purchase.models import PurchasedItem as Item
from saleor.purchase.models import PurchaseVariantHistoryEntry as HistoryEntry

from ...product.models import (
    Stock,
    ProductVariant
)
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


class ItemSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField()
    max_quantity = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()
    stock_id = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'order',
            'sku',
            'quantity',
            'max_quantity',
            'stock_quantity',
            'stock_id',
            'unit_cost',
            'total_cost',
            'unit_purchase',
            'total_purchase',
            'product_name',
        )

    def get_quantity(self, obj):
        quantity = obj.returnable_quantity() if obj.returnable_quantity() < obj.get_quantity() else obj.get_quantity()
        return quantity

    def get_stock_id(self, obj):
        try:
            return obj.stock.id
        except:
            return 0

    def get_stock_quantity(self, obj):
        try:
            return obj.stock.quantity
        except:
            return 0

    def get_max_quantity(self, obj):
        quantity = obj.quantity if obj.quantity < obj.get_quantity() else obj.get_quantity()
        return quantity


class HistorySerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = HistoryEntry
        fields = (
            'tendered',
            'balance',
            'payment_name',
            'transaction_number',
            'date'
        )

    def get_date(self, obj):
        return localize(obj.created)


class TableCreateSerializer(serializers.ModelSerializer):
    """
    Create stock purchase:
    item: JSON: purchased stock items
    history: JSON: Payment history for purchase instance
           : include payment options, transaction number & amount values
    """
    item = JSONField()
    history = JSONField()

    class Meta:
        model = Table
        fields = (
            'id',
            'user',
            'supplier',
            'status',
            'quantity',
            'total_net',
            'amount_paid',
            'balance',
            'item',
            'history'
        )

    def create(self, validated_data):
        # new purchase instance
        # Table.objects.all().delete()
        instance = Table()
        # generate invoice number from last id
        try:
            invoice_number = Table.objects.latest('id').id
        except:
            invoice_number = 1
        invoice_number = 'INV/' + str(invoice_number) + str(random.randint(2, 10))

        # detect credit & fully paid transaction
        if validated_data.get('amount_paid') < validated_data.get('total_net'):
            # credit sale
            instance.status = 'payment-pending'
            instance.balance = validated_data.get('balance')
            instance.amount_paid = validated_data.get('amount_paid')
        else:
            instance.status = 'fully-paid'
            instance.amount_paid = validated_data.get('total_net')
            instance.balance = 0
        instance.supplier = validated_data.get('supplier')
        instance.invoice_number = invoice_number
        instance.total_net = validated_data.get('total_net')
        instance.sub_total = validated_data.get('sub_total')
        instance.quantity = validated_data.get('quantity')
        instance.payment_data = validated_data.get('payment_data')
        instance.history = validated_data['history']
        instance.item = validated_data['item']
        instance.save()

        # create history
        # try:
        # histories = json.loads(validated_data.pop('purchase_history'))
        histories = validated_data['history']
        for item in histories:
            # create history
            history = HistoryEntry()
            history.purchase = instance
            history.tendered = item['tendered']
            history.payment_name = item['payment_name']
            history.transaction_number = item['transaction_number']
            history.save()
        # except Exception as e:
        #     raise ValidationError(e)
        # add stock & quantity
        try:
            items = validated_data['item']
        except Exception as e:
            raise ValidationError(e)

        def update_all_stock_price_override(variant, price_override):
            variant.stock.all().update(price_override=price_override)

        def create_variant_stock(item, variant):
            stock = Stock()
            stock.variant = variant
            stock.quantity = item['qty']
            stock.cost_price = item['cost_price']
            stock.price_override = item.get('price_override', 0)
            try:
                stock.minimum_price = item['minimum_price']
            except:
                stock.minimum_price = 0
            try:
                stock.wholesale_override = item['wholesale_override']
            except:
                stock.wholesale_override = item['price_override']
            if item['low_stock_threshold']:
                stock.low_stock_threshold = item['low_stock_threshold']

            stock.save()
            return stock

        for item in items:
            new_created = False
            if not item.get('price_override'):
                item['price_override'] = 0
            variant = ProductVariant.objects.get(sku=item.get('sku'))

            try:
                stock = Stock.objects.filter(variant__sku=item['sku']).last()
                if stock.cost_price.gross != item['cost_price']:
                    if not new_created:
                        # ('create a new  variant')
                        new_stock = create_variant_stock(item, variant)
                        new_created = True
                if stock.price_override.gross != item['price_override']:
                    # each stock should have similar price
                    update_all_stock_price_override(variant, item['price_override'])
                    if not new_created:
                        # ('create a new  variant')
                        new_stock = create_variant_stock(item, variant)
                        new_created = True
                else:
                    print('do not create new variant')
                if not new_created:
                    Stock.objects.increase_stock(stock, item['qty'])
                    new_stock = stock
            except Exception as e:
                print(e)
                # create new stock
                if not new_created:
                    stock = Stock()
                    stock.variant = variant
                    stock.quantity = item['qty']
                    stock.cost_price = item['cost_price']
                    stock.price_override = item.get('price_override', 0)
                    try:
                        stock.minimum_price = item['minimum_price']
                    except:
                        stock.minimum_price = 0
                    try:
                        stock.wholesale_override = item['wholesale_override']
                    except:
                        stock.wholesale_override = item.get('price_override', 0)
                    if item['low_stock_threshold']:
                        stock.low_stock_threshold = item['low_stock_threshold']
                    stock.save()
                    update_all_stock_price_override(stock.variant, item.get('price_override', 0))
                    new_stock = stock

                logger.error(e)
            # create purchased items
            single_item = Item()
            single_item.stock = new_stock
            single_item.purchase = instance
            single_item.total_cost = item['total_cost']
            single_item.unit_cost = item['cost_price']
            single_item.wholesale_price = item.get('wholesale_price')
            single_item.minimum_price = item.get('minimum_price')
            single_item.low_stock_threshold = item.get('low_stock_threshold')
            single_item.price_override = item.get('price_override', 0)
            single_item.product_name = item['product_name']
            single_item.sku = item['sku']
            single_item.quantity = item['qty']
            single_item.order = 1
            single_item.save()
        return instance


class TableListSerializer(serializers.ModelSerializer):
    single_url = HyperlinkedIdentityField(view_name='dashboard:purchase-variant-single')
    detail_url = HyperlinkedIdentityField(view_name='dashboard:purchase-variant-detail')
    purchased_item = ItemSerializer(many=True)
    purchase_history = HistorySerializer(many=True)
    supplier_name = serializers.SerializerMethodField()
    total_purchases = SerializerMethodField()
    total_credit = SerializerMethodField()
    total_cost = SerializerMethodField()
    total_quantity = SerializerMethodField()
    date = serializers.SerializerMethodField()
    instance_status = SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'id',
            'user',
            'instance_status',
            'supplier_name',
            'total_net',
            'amount_paid',
            'invoice_number',
            'balance',
            'quantity',
            'total_cost',
            'total_quantity',
            'total_purchases',
            'total_credit',
            'single_url',
            'detail_url',
            'purchased_item',
            'purchase_history',
            'date'
        )

    def get_instance_status(self, obj):
        if obj.status == 'fully-paid':
            return '<span class ="text-success ">fully paid </span>'
        else:
            return '<span class ="badge badge-flat border-warning text-warning-600" > Pending..</span>'

    def get_total_quantity(self, obj):
        try:
            return "{:,}".format(Table.objects.total_quantity(obj))
        except:
            return 0

    def get_total_purchases(self, obj):
        try:
            return "{:,}".format(Table.objects.total_purchases(obj))
        except:
            return 0

    def get_total_credit(self, obj):
        try:
            return "{:,}".format(Table.objects.total_credit(obj))
        except:
            return 0

    def get_total_cost(self, obj):
        try:
            return "{:,}".format(Table.objects.total_cost(obj))
        except:
            return 0

    def get_supplier_name(self, obj):
        try:
            return obj.supplier.name
        except:
            return ''

    def get_date(self, obj):
        return localize(obj.created)
