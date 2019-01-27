import datetime
from decimal import Decimal
from django.db.models import Q, F, Sum, Count
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.dateformat import DateFormat
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination
from ...product.models import AttributeChoiceValue
from ...discount.models import Sale as Discount
from ...sale.models import Sales
from ...sale.models import SoldItem as Item
from ...orders.models import *
from .serializers import (
    ListSaleSerializer,
    CreateSaleSerializer,
    ItemSerializer,
    DiscountedItemSerializer
)
from .serializers import ListOrderSerializer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()

factory = APIRequestFactory()
request = factory.get('/')
serializer_context = {
    'request': Request(request),
}


class SaleDetailAPIView(generics.RetrieveAPIView):
    queryset = Sales.objects.all()
    serializer_class = ListSaleSerializer


class SaleCreateAPIView(generics.CreateAPIView):
    queryset = Sales.objects.all()
    serializer_class = CreateSaleSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SaleListAPIView(generics.ListAPIView):
    serializer_class = ListSaleSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Sales.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query)
            ).distinct()
        return queryset_list


class ListAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
    """
    serializer_class = ListSaleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Sales.objects.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct(
                    'car').select_related()
            else:
                queryset_list = Sales.objects.all.select_related()
        except Exception as e:
            queryset_list = Sales.objects.all()

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date__icontains=self.request.GET.get('date'))

        if self.request.GET.get('user'):
            queryset_list = queryset_list.filter(user__pk=int(self.request.GET.get('user')))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query))
        return queryset_list.order_by('-id')


class ListItemAPIView(generics.ListAPIView):
    """
        list details
        GET /api/sale/list/items/
    """
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        queryset_list = Item.objects.filter(quantity__gt=F('returned_quantity'))
        try:
            if self.kwargs['pk']:
                queryset_list = queryset_list.filter(sales__pk=self.kwargs['pk']).select_related()

        except Exception as e:
            pass

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date__icontains=self.request.GET.get('date'))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(product_name__icontains=query) |
                Q(sku__icontains=query)
            )
        return queryset_list.order_by('-id')


class ItemListAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        """
        Return a list of all sales.
        """
        key = ''
        date = ''
        if self.kwargs['pk']:
            key = self.kwargs['pk']
        if self.request.GET.get('date'):
            date = self.request.GET.get('date')
            summary = Item.objects.values('created', 'product_name', 'attributes').filter(
                created__icontains=date).filter(attributes__has_key=key)

        else:
            summary = Item.objects.values('product_name', 'attributes').filter(attributes__has_key=key)
        report = []
        checker = []
        for i in summary:
            name = AttributeChoiceValue.objects.get(pk=int(i['attributes'][key])).name
            temp2 = {}
            temp = eval(
                "Item.objects.values('created', 'product_name', 'total_cost', 'quantity', 'attributes').filter(created__icontains='" + date + "', attributes__" + key + "=" +
                i['attributes'][
                    key] + ").annotate(c=Count('attributes', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity'))")
            quantity = 0
            sum = 0
            for count in temp:
                quantity += count['quantity__sum']
                sum += count['total_cost__sum']
            temp2['quantity'] = quantity
            temp2['sum'] = sum
            temp2['attribute_value'] = name
            if i['attributes'][key] not in checker:
                report.append(temp2)
                checker.append(i['attributes'][key])
        return Response(report)


class SoldItemListAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        """
        Return a list of all sales.
        """
        key = ''

        if self.request.GET.get('date'):
            date = self.request.GET.get('date')
        else:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

        summary = Item.objects.filter(created__icontains=date).values('product_name', 'product_category').annotate(
            c=Count('product_name', distinct=True)) \
            .annotate(Sum('total_cost')) \
            .annotate(Sum('quantity')).order_by('-quantity__sum')

        summary = summary.annotate(tax=F('total_cost__sum') * 0.16)
        total_sales = summary.aggregate(Sum("total_cost__sum"))["total_cost__sum__sum"]
        total_tax = summary.aggregate(Sum("tax"))["tax__sum"]

        # payment options calculations
        sales_qs = Sales.objects.filter(created__icontains=date)
        payments = []

        for i in sales_qs:
            for j in i.payment_data:
                try:
                    payment_name = PaymentOption.objects.get(pk=int(j['payment_id'])).name
                except:
                    payment_name = int(j['payment_id'])

                if any(d['payment_id'] == int(j['payment_id']) for d in payments):
                    for d in payments:
                        if d['payment_id'] == int(j['payment_id']):
                            d['value'] += Decimal(j['value'])
                else:
                    payments.append({"payment_id": int(j["payment_id"]), "value": Decimal(j["value"]), "name": payment_name})

        response = {
            "items": summary,
            "total_sales": total_sales,
            "total_tax": total_tax,
            "payments": payments
        }

        return Response(response)


class SaleMarginListAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        """
            Return a list of all sales.
        """
        if self.request.GET.get('date'):
            date = self.request.GET.get('date')
            summary = Item.objects.filter(created__icontains=date).values('product_name',
                                                                          'product_category').annotate(
                c=Count('product_name', distinct=True)) \
                .annotate(Sum('total_cost')) \
                .annotate(Sum('total_purchase')) \
                .annotate(Sum('quantity')).order_by('-quantity__sum')
        else:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')
            summary = Item.objects.filter(created__icontains=date) \
                .values('product_name', 'product_category').annotate(
                c=Count('product_name', distinct=True)) \
                .annotate(Sum('total_cost')) \
                .annotate(Sum('total_purchase')) \
                .annotate(Sum('quantity')).order_by('-quantity__sum')
        total_sale = 0
        total_cost = 0
        result = {}
        for sale in summary:
            total_sale += sale['total_cost__sum']
            total_cost += sale['total_purchase__sum']
        result['total_cost'] = total_cost
        result['total_sale'] = total_sale
        result['margin'] = total_sale - total_cost

        return Response(result)


class UserSaleAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        """
        Return a list of all orders grouped in complete, incomplete and cancelled.
        """

        if self.request.GET.get('date'):
            date = self.request.GET.get('date')
        else:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

        orders = Orders.objects.filter(created__icontains=date)

        user_id = self.request.GET.get('user')
        user = None
        if user_id:
            orders = orders.filter(user__pk=int(user_id))
            try:
                user = User.objects.get(pk=int(user_id)).name
            except:
                user = "None"

        complete_orders = orders.filter(status="fully-paid")
        incomplete_orders = orders.filter(status="payment-pending")
        cancelled_orders = orders.filter(status="cancelled")

        # aggregates
        complete_totals = complete_orders.aggregate(Sum("total_net"))["total_net__sum"]
        incomplete_totals = incomplete_orders.aggregate(Sum("total_net"))["total_net__sum"]
        cancelled_totals = cancelled_orders.aggregate(Sum("total_net"))["total_net__sum"]

        expected_sales = 0
        if complete_totals:
            expected_sales += complete_totals
        if incomplete_totals:
            expected_sales += incomplete_totals

        complete_serializer = ListOrderSerializer(complete_orders, many=True)
        incomplete_serializer = ListOrderSerializer(incomplete_orders, many=True)
        cancelled_serializer = ListOrderSerializer(cancelled_orders, many=True)

        complete_orders = complete_serializer.data
        incomplete_orders = incomplete_serializer.data
        cancelled_orders = cancelled_serializer.data

        response = {
            "expected_sales": expected_sales,
            "date": date,
            "user": user,
            "complete_orders": {
                "orders": complete_orders,
                "total_sales": complete_totals
            },
            "incomplete_orders": {
                "orders": incomplete_orders,
                "total_sales": incomplete_totals
            },
            "cancelled_orders": {
                "orders": cancelled_orders,
                "total_sales": cancelled_totals
            }
        }

        return Response(response)


class DiscountSaleAPIView(APIView):
    def get(self, request, format=None, **kwargs):
        """
        Return a list of all orders grouped in complete, incomplete and cancelled.
        """

        if self.request.GET.get('date'):
            date = self.request.GET.get('date')
        else:
            date = DateFormat(datetime.datetime.today()).format('Y-m-d')

        discount_id = self.request.GET.get('discount')
        discount_amount = 0

        try:
            discount = Discount.objects.get(pk=int(discount_id))
            description = str(discount.quantity) + ' items @' + str(discount.value)
            discount_amount = discount.value
        except Exception as e:
            discount = None
            description = "Default Discount"
            logger.info('Error in getting discount using id: ' + str(discount_id) + ', Exception: ' + str(e))

        items = Item.objects.filter(created__icontains=date, discount_set_status=True)
        v = []
        for i in items:
            setattr(i, "discount_unit_amount", discount_amount)
            v.append(i)

        total_discount_amount = 0
        if discount:
            items = items.filter(discount_id=str(discount.id))
            total_discount_amount = items.aggregate(Sum("discount_total"))["discount_total__sum"]

        extracted_items = items.values(
            'sku',
            'product_name',
            'product_category',
            'unit_cost',
            'discount_set_status').annotate(
            count=Count('product_name', distinct=True)).annotate(
            discount_total=Sum('discount_total')).annotate(
            discount_quantity=Sum('discount_quantity'))

        final_items = []
        for i in extracted_items:
            i["discount_price"] = discount_amount
            final_items.append(i)

        response = {
            "total": total_discount_amount,
            "description": description,
            "items": final_items,
            "date": datetime.datetime.strptime(date, '%Y-%m-%d').strftime(
                                     '%b %d, %Y')
        }

        return Response(response)

