from django.db.models import Q
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import serializers
from ...orders.models import Orders, OrderedItem, CancelledOrder
from ...product.models import Stock
from ...sale.models import (
    Sales,
    SoldItem,
    Terminal,
    TerminalHistoryEntry,
    DrawerCash,
    PaymentOption
)

from .serializers import (
    ListOrderSerializer,
    OrderSerializer,
    OrderUpdateSerializer,
    ListOrderItemSerializer,
    OrderReadyOrCollectedSerializer,
    SearchListOrderSerializer,
    ListCancelledOrderSerializer,
    MenuSearchListOrderSerializer,
    ItemVerifierSerializer
)
from ...decorators import user_trail
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from saleor.countertransfer.models import CounterTransferItems as Item
from saleor.menutransfer.models import TransferItems as MenuItem
from saleor.counter.models import Counter
from saleor.kitchen.models import Kitchen
from structlog import get_logger
import json

logger = get_logger(__name__)

User = get_user_model()

factory = APIRequestFactory()
request = factory.get('/')
serializer_context = {
    'request': Request(request),
}


def return_to_stock(ordered_items):
    for item in ordered_items:
        if item.counter:
            # return to stock
            try:
                stock = Item.objects.get(pk=item.transfer_id)
                if item:
                    Item.objects.increase_stock(stock, item.quantity)
            except:
                pass
        elif item.kitchen:
            # return to menu stock
            try:
                stock = MenuItem.objects.get(pk=item.transfer_id)
                if item:
                    MenuItem.objects.increase_stock(stock, item.quantity)
            except:
                pass


class DestroyView(generics.DestroyAPIView):
    queryset = Orders.objects.all()

    def perform_destroy(self, instance):
        ordered_items = instance.ordered_items.all()
        # return stock/menu items then delete
        return_to_stock(ordered_items)
        order = CancelledOrder()
        order.order_id = instance.id

        # convert the data to json
        data = serializers.serialize('json', [instance, ])
        stru = json.loads(data)
        data = json.dumps(stru[0])

        order.payload = data # extract data
        order.save()

        instance.status = 'cancelled'
        instance.save()

        user_trail(self.request.user.name,
                   'cancelled order:#' + str(instance.invoice_number), 'delete')

        logger.info('User: ' + str(self.request.user) +
                    'cancelled order:#' + str(instance.invoice_number))

        return Response({}, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(generics.RetrieveAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer


class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Orders.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        if serializer.data['status'] == 'fully-paid':
            send_to_sale(instance)

        if serializer.data['status'] == 'credit':

            logger.info('User: ' + str(self.request.user) +
                        ' made a takeaway order sale:' + str(serializer.data['invoice_number']))
            terminal = Terminal.objects.get(pk=int(serializer.data['terminal']))

            trail = 'User: ' + str(self.request.user) + \
                    ' created a takeaway order sale :' + str(serializer.data['invoice_number']) + \
                    ' Net#: ' + str(serializer.data['total_net']) + \
                    ' Amount paid#:' + str(serializer.data['amount_paid'])

            user_trail(self.request.user.name,
                       'made a takeaway sale:#' + str(serializer.data['invoice_number']) +
                       ' sale worth: ' + str(serializer.data['total_net']), 'add')

            TerminalHistoryEntry.objects.create(
                terminal=terminal,
                comment=trail,
                crud='deposit',
                user=self.request.user
            )
            DrawerCash.objects.create(
                manager=self.request.user,
                user=self.request.user,
                terminal=terminal,
                amount=serializer.data['amount_paid'],
                trans_type='sale')


class OrderListAPIView(generics.ListAPIView):
    serializer_class = ListOrderSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Orders.objects.all()
        query = self.request.GET.get('q')
        user = self.request.GET.get('user')
        date = self.request.GET.get('date')
        
        if date:
            queryset_list = queryset_list.filter(created__icontains=date)

        if user:
            queryset_list = queryset_list.filter(user__pk=int(user))

        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)
            ).distinct()

        return queryset_list


class OrderItemsListAPIView(generics.ListAPIView):
    serializer_class = ListOrderItemSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = OrderedItem.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(product_name__icontains=query)
            ).distinct()
        return queryset_list


class OrderStatusListAPIView(generics.ListAPIView):
    serializer_class = ListOrderSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Orders.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(status=query)
            ).distinct()
        return queryset_list


class SalePointOrdersListAPIView(generics.ListAPIView):
    serializer_class = ListOrderSerializer
    queryset = Orders.objects.all().order_by('id')

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        query = self.request.GET.get('q')
        if query:
            queryset = self.get_queryset().filter(sale_point__pk=pk).filter(status=query)
        else:
            queryset = self.get_queryset().filter(sale_point__pk=pk)
        serializer = ListOrderSerializer(queryset, many=True, context=serializer_context)
        return Response(serializer.data)


class SalePointNextOrdersListAPIView(generics.ListAPIView):
    """
        list new ordered items
        @:param q is order status
        @:param pk sale point id
        @:param order_pk order start query

        GET /api/order/sale-point/2/47?q=pending-payment
        payload Json: /payload/getnewerorders.json
    """
    serializer_class = ListOrderSerializer
    queryset = Orders.objects.all()

    def list(self, request, pk=None, order_pk=None):
        serializer_context = {
            'request': Request(request),
        }
        query = self.request.GET.get('q')
        queryset = self.get_queryset().filter(
            Q(sale_point__pk=pk) and
            Q(pk__gt=order_pk)
        )
        if query:
            queryset = self.get_queryset().filter(
                status=query,
                sale_point__pk=pk,
                pk__gt=order_pk
            )

        serializer = ListOrderSerializer(queryset, many=True, context=serializer_context)
        return Response(serializer.data)


class SalePointOrdersItemListAPIView(generics.ListAPIView):
    """
        list ordered items where q is order status
        1 is sale point id
        GET /api/order/sale-point-items/1?q=fully-paid
        payload Json: /payload/orderditems.json
    """

    serializer_class = ListOrderItemSerializer
    queryset = OrderedItem.objects.all().order_by('-id')

    def list(self, request, pk=None):
        # Note the use of `get_queryset()` instead of `self.queryset`
        query = self.request.GET.get('q')
        if query:
            queryset = self.get_queryset().filter(sale_point__pk=pk).filter(orders__status=query)
        else:
            queryset = self.get_queryset().filter(sale_point__pk=pk)
        serializer = ListOrderItemSerializer(queryset, many=True)
        return Response(serializer.data)


class TableOrdersListAPIView(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = ListOrderSerializer(instance=queryset, context=serializer_context)

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        # Note the use of `get_queryset()` instead of `self.queryset`
        query = self.request.GET.get('q')
        order = self.request.GET.get('order')

        if order and query:
            queryset = self.get_queryset().filter(
                Q(table__pk=pk) & Q(invoice_number=order)
            )
        elif query:
            queryset = self.get_queryset().filter(table__pk=pk).filter(status=query)
        else:
            queryset = self.get_queryset().filter(table__pk=pk)

        serializer = ListOrderSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        if request.data.get('status') == 'delete':
            orders_to_be_deleted = []
            # delete each order and return orders to counter/menu transfer
            if request.data.get('orders'):
                for order in request.data.get('orders'):
                    instance = Orders.objects.get(invoice_number=str(order))
                    ordered_items = instance.ordered_items.all()
                    # return stock/menu items then delete
                    return_to_stock(ordered_items)
                    instance.status = "Cancelled"
                    instance.save()
                    orders_to_be_deleted.append(order)
                user_trail(self.request.user.name,
                       'cancelled orders :#' + str(orders_to_be_deleted), 'delete')
        return Response("successfully delete, status=204")


class SearchOrdersListAPIView(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = SearchListOrderSerializer(instance=queryset, context=serializer_context)

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
            'pk': pk,
            'counter': self.request.GET.get('counter', ""),
            'point': self.request.GET.get('point'),
            'status': self.request.GET.get('status')
        }
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = Orders.objects.filter(status="payment-pending")
        counter = self.request.GET.get("counter", "")
        point = self.request.GET.get("point", "")
        status = self.request.GET.get('status')
        user_id = self.request.GET.get('user')
        readyStatusBoolean = False
        collectedStatusBoolean = False
        if status:
            if status.lower() == "collected" or status.lower() == "not collected":
                if status.lower() == "collected":
                    collectedStatusBoolean = True
                elif status.lower() == "not collected":
                    collectedStatusBoolean = False
                set_orders = []
                for i in queryset:
                    if point == "counter":
                        products_count = OrderedItem.objects.filter(orders=i, collected=collectedStatusBoolean,
                                                                    counter__pk=counter).count()
                    elif point == "kitchen":
                        products_count = OrderedItem.objects.filter(orders=i, collected=collectedStatusBoolean,
                                                                    kitchen__pk=counter).count()
                    else:
                        products_count = OrderedItem.objects.filter(orders=i, collected=collectedStatusBoolean).count()
                    if products_count >= 1:
                        set_orders.append(i.pk)

                queryset = queryset.filter(pk__in=set_orders)

            elif status.lower() == "ready" or status.lower() == "not ready":
                if status.lower() == "ready":
                    readyStatusBoolean = True
                elif status.lower() == "not ready":
                    readyStatusBoolean = False
                set_orders = []
                for i in queryset:
                    if point == "counter":
                        products_count = OrderedItem.objects.filter(orders=i, ready=readyStatusBoolean,
                                                                    counter__pk=counter).count()
                    elif point == "kitchen":
                        products_count = OrderedItem.objects.filter(orders=i, ready=readyStatusBoolean,
                                                                    kitchen__pk=counter).count()
                    else:
                        products_count = OrderedItem.objects.filter(orders=i, ready=readyStatusBoolean).count()
                    if products_count >= 1:
                        set_orders.append(i.pk)

                queryset = queryset.filter(pk__in=set_orders)
        else:
            queryset = queryset.filter(status='payment-pending')

        if user_id:
            queryset = queryset.filter(user__pk=int(user_id))

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(status='payment-pending') |
                (Q(status='fully-paid') & Q(table__isnull=True) & Q(room__isnull=True)) |
                Q(invoice_number__icontains=query) |
                Q(room__name__icontains=query) |
                Q(table__name__icontains=query) |
                Q(user__name__icontains=query)).distinct()
        else:
            queryset = queryset.distinct()

        serializer = SearchListOrderSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        orders = Orders.objects.filter(table__pk=pk)
        orders.delete()
        return Response("successfully delete, status=204")


class RoomOrdersListAPIView(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = ListOrderSerializer(instance=queryset, context=serializer_context)

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        # Note the use of `get_queryset()` instead of `self.queryset`
        query = self.request.GET.get('q')
        if query:
            queryset = self.get_queryset().filter(room__pk=pk).filter(status=query)
        else:
            queryset = self.get_queryset().filter(room__pk=pk)
        serializer = ListOrderSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        orders = Orders.objects.filter(room__pk=pk)
        orders.delete()
        return Response("successfully delete, status=204")


class OrderUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
        update order details

        @:param pk order id
        @:method PUT

        PUT /api/order/update-order/62/
        payload Json: /payload/update_order.json
    """
    queryset = Orders.objects.all()
    serializer_class = OrderUpdateSerializer

    def perform_update(self, serializer):
        instance = serializer.save(user=self.request.user)
        if instance.status == 'fully-paid':
            send_to_sale(instance)

            logger.info('User: ' + str(self.request.user) +
                        ' made a order sale:' + str(serializer.data['invoice_number']))
            terminal = Terminal.objects.get(pk=int(serializer.data['terminal']))

            trail = 'User: ' + str(self.request.user) + \
                    ' updated a order sale :' + str(serializer.data['invoice_number']) + \
                    ' Net#: ' + str(serializer.data['total_net']) + \
                    ' Amount paid#:' + str(serializer.data['amount_paid'])

            user_trail(self.request.user.name,
                       'made a sale:#' + str(serializer.data['invoice_number']) +
                       ' sale worth: ' + str(serializer.data['total_net']), 'add')

            TerminalHistoryEntry.objects.create(
                terminal=terminal,
                comment=trail,
                crud='deposit',
                user=self.request.user
            )
            DrawerCash.objects.create(
                manager=self.request.user,
                user=self.request.user,
                terminal=terminal,
                amount=serializer.data['amount_paid'],
                trans_type='sale')

        elif instance.status.lower() == 'cancelled':

            order = CancelledOrder()
            order.order_id = serializer.data['id']
            order.payload = serializer.data
            order.save()

            instance.delete()

            user_trail(self.request.user.name,
                       'cancelled order:#' + str(serializer.data['invoice_number']), 'delete')

            logger.info('User: ' + str(self.request.user) +
                        'cancelled order:#' + str(serializer.data['invoice_number']))

            return 'Successfully deleted, status: 204'
        elif instance.status == 'credited':
            user_trail(self.request.user.name,
                       'credited order:#' + str(serializer.data['invoice_number']), 'delete')

            logger.info('User: ' + str(self.request.user) +
                        'credited order:#' + str(serializer.data['invoice_number']))


def send_to_sale(credit):
    sale = Sales()
    sale.created = credit.created
    sale.user = credit.user
    sale.invoice_number = credit.invoice_number
    sale.total_net = credit.total_net
    sale.sub_total = credit.sub_total
    sale.balance = credit.balance
    sale.terminal = credit.terminal
    sale.amount_paid = credit.amount_paid
    sale.status = credit.status
    sale.payment_data = credit.payment_data
    if credit.customer_name:
        sale.customer_name = credit.customer_name
    if credit.customer:
        sale.customer = credit.customer

    try:
        sale.table = credit.table
        sale.room = credit.room
        sale.carry = 'Sitting'
    except Exception as e:
        sale.carry = 'Take Away'
    sale.total_tax = credit.total_tax
    sale.save()

    for option in credit.payment_data:
        try:
            pay_opt = PaymentOption.objects.get(pk=int(option['payment_id']))
            sale.payment_options.add(pay_opt)
        except Exception as e:
            logger.error("error adding options " + str(e))

    for item in credit.items():
        new_item = SoldItem.objects.create(
            sales=sale,
            sku=item.sku,
            quantity=item.quantity,
            product_name=item.product_name,
            total_cost=item.total_cost,
            unit_cost=item.unit_cost,
            product_category=item.product_category
        )
        new_item.counter = item.counter
        new_item.transfer_id = item.transfer_id
        new_item.order_id = item.id
        new_item.attributes = item.attributes
        new_item.unit_purchase = item.unit_purchase
        new_item.total_purchase = item.total_purchase
        if item.discount_id:
            new_item.discount_id = item.discount_id.pk
        new_item.discount_quantity = item.discount_quantity
        new_item.discount_total = item.discount_total
        new_item.discount_set_status = item.discount_set_status
        new_item.cold = item.cold
        new_item.cold_quantity = item.cold_quantity

        if item.counter:
            try:
                stock = Stock.objects.filter(sku=item.sku).first()
                new_item.minimum_price = stock.minimum_price
                new_item.wholesale_override = stock.wholesale_override
                new_item.low_stock_threshold = stock.low_stock_threshold
                new_item.unit_purchase = stock.cost_price
            except Exception as e:
                pass
        elif item.kitchen:
            new_item.is_stock = False
        else:
            pass
        new_item.kitchen = item.kitchen
        new_item.save()


class OrderReadyOrCollectedAPIView(generics.RetrieveUpdateAPIView):
    """
        update order details

        @:param pk order id
        @:method PUT

        PUT /api/order/update-order/62/
        payload Json: /payload/update_order.json
    """
    queryset = Orders.objects.all()
    serializer_class = OrderReadyOrCollectedSerializer


class CancelledOrderListAPIView(generics.ListAPIView):
    serializer_class = ListCancelledOrderSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = CancelledOrder.objects.all()
        return queryset_list


class SearchMenuOrderListAPIView(generics.ListAPIView):
    queryset = Orders.objects.all()
    serializer_class = MenuSearchListOrderSerializer(instance=queryset, context=serializer_context)

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
            'pk': pk,
            'status': self.request.GET.get('status')
        }

        queryset = Orders.objects.filter(status="payment-pending")
        user_id = self.request.GET.get('user')
        query = self.request.GET.get('q')

        if user_id:
            queryset = queryset.filter(user__pk=int(user_id))

        if query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=query) |
                Q(room__name__icontains=query) |
                Q(table__name__icontains=query) |
                Q(user__name__icontains=query)).distinct()
        else:
            queryset = queryset.distinct()

        serializer = MenuSearchListOrderSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)


class OrderSavedConfirmationAPIView(APIView):
    def get(self, request):

        order_json = json.loads(self.request.GET.get('order_json'))

        order_invoice_number = order_json['invoice_number']
        order_items = order_json['ordered_items']
        successful_items = []
        failed_items = []
        order_created_status = False

        # check if order exists
        try:
            order_checker = Orders.objects.get(invoice_number=order_invoice_number)
            order_created_status = True
            # go through the items and check if the items are available in db
            for i in order_items:

                stock_item = Item.objects.get(pk=int(i['transfer_id']))
                stock_quantity = stock_item.qty

                try:
                    counter = Counter.objects.get(pk=int(i['counter'])).name
                except:
                    counter = None

                try:
                    kitchen = Kitchen.objects.get(pk=int(i['kitchen'])).name
                except:
                    kitchen = None

                try:
                    order_item_qty = OrderedItem.objects.get(
                        orders=order_checker,
                        product_name=i['product_name'],
                        sku=i['sku'],
                        transfer_id=int(i['transfer_id'])
                    ).quantity
                except:
                    order_item_qty = 0

                try:
                    ordered_item_checker = OrderedItem.objects.get(
                        orders=order_checker,
                        product_name=i['product_name'],
                        sku=i['sku'],
                        transfer_id=int(i['transfer_id']),
                        quantity=int(i['quantity'])
                    )

                    if ordered_item_checker:
                        item_record = {
                            'quantity': i['quantity'],
                            'current_quantity': stock_quantity,
                            'order_item_qty': order_item_qty,
                            'product_name': i['product_name'],
                            'counter': counter,
                            'kitchen': kitchen
                        }
                        successful_items.append(item_record)
                except Exception as e:
                    item_record = {
                        "quantity": i['quantity'],
                        "current_quantity": stock_quantity,
                        'order_item_qty': order_item_qty,
                        "product_name": i['product_name'],
                        'counter': counter,
                        'kitchen': kitchen
                    }
                    failed_items.append(item_record)
        except Exception as e:
            for i in order_items:
                stock_item = Item.objects.get(pk=int(i['transfer_id']))
                stock_quantity = stock_item.qty
                try:
                    counter = Counter.objects.get(pk=int(i['counter'])).name
                except:
                    counter = None

                try:
                    kitchen = Kitchen.objects.get(pk=int(i['kitchen'])).name
                except:
                    kitchen = None

                item_record = {
                    "quantity": i['quantity'],
                    "current_quantity": stock_quantity,
                    'order_item_qty': 0,
                    "product_name": i['product_name'],
                    'counter': counter,
                    'kitchen': kitchen
                }
                failed_items.append(item_record)

        order_detail = {
            "order_created_status": order_created_status,
            "failed_items": failed_items
        }

        serializer = ItemVerifierSerializer(order_detail)
        return Response(serializer.data)

