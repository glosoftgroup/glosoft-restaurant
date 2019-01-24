import datetime
from datetime import date
from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from .pagination import PostLimitOffsetPagination

from saleor.product.models import ProductVariant
from saleor.product.models import Stock as Table
from saleor.countertransfer.models import CounterTransferItems as CounterItems
from saleor.menutransfer.models import TransferItems as MenuItem
from saleor.core.utils.closing_time import is_business_time
from .serializers import (
    CreateListSerializer,
    TableListSerializer,
    UpdateSerializer,
    SearchTransferredStockListSerializer
)
from saleor.discount.models import Sale
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()
request = APIRequestFactory().get('/')
serializer_context = {
    'request': Request(request),
}


class CreateAPIView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = CreateListSerializer


class DestroyView(generics.DestroyAPIView):
    queryset = Table.objects.all()


class ListAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
    """
    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        queryset_list = Table.objects.filter(quantity__gte=1).select_related()

        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if category:
            queryset_list = queryset_list.filter(variant__product__categories__id=category)
        if query:
            queryset_list = queryset_list.filter(
                Q(variant__sku__icontains=query) |
                Q(variant__product__name__icontains=query) |
                Q(variant__product__description__icontains=query)
            ).distinct()
        return queryset_list


class UpdateAPIView(generics.RetrieveUpdateAPIView):
    """
        update instance details
        @:param pk house id
        @:method PUT

        PUT /api/house/update/
        payload Json: /payload/update.json
    """
    queryset = Table.objects.all()
    serializer_class = UpdateSerializer


class SearchTransferredStockListAPIView(APIView):
    def get(self, request):

        query = self.request.GET.get('q', '')
        today = datetime.date.today()
        show_yesterday = is_business_time()
        today = datetime.date.today()
        if show_yesterday:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
        else:
            yesterday = today
        all_counter_menu_stock = []
        """ get the counter stocks """
        try:
            counter_stock = CounterItems.objects.filter(
                Q(transfer__date=today) |
                Q(transfer__date=yesterday)
            ).filter(qty__gte=1).distinct('stock').select_related()

            if query:
                counter_stock = counter_stock.filter(
                    Q(stock__variant__sku__icontains=query) |
                    Q(stock__variant__product__name__icontains=query) |
                    Q(counter__name__icontains=query)).order_by('stock')

            if counter_stock.exists():
                for i in counter_stock:
                    """ set the json data fields 
                        using getCounterItemsJsonData(obj)
                    """
                    all_counter_menu_stock.append(getCounterItemsJsonData(i))


        except Exception as e:
            """ log error """
            logger.info('Error in getting counter stock: ' + str(e))
            pass

        """ get the menu stocks """
        try:
            menu_stock = MenuItem.objects.filter(
                Q(transfer__date=today) |
                Q(transfer__date=yesterday)
            ).filter(qty__gte=1).distinct('menu').select_related()
            print (menu_stock)
            if query:
                menu_stock = menu_stock.filter(
                    Q(menu__category__name__icontains=query) |
                    Q(name__icontains=query) |
                    Q(counter__name__icontains=query) |
                    Q(menu__name__icontains=query) |
                    Q(menu__id__icontains=query)).order_by('menu')

            if menu_stock.exists():
                for i in menu_stock:
                    """ set the json data fields 
                        using getMenuItemsJsonData(obj)
                    """
                    all_counter_menu_stock.append(getMenuItemsJsonData(i))


        except Exception as e:
            """ log error """
            logger.info('Error in getting menu stock: ' + str(e))
            pass

        serializer = SearchTransferredStockListSerializer(all_counter_menu_stock, many=True)
        return Response(serializer.data)


""" set the counter items json """


def getCounterItemsJsonData(obj):
    """ id """
    id = obj.id

    """ sku """
    try:
        sku = obj.stock.variant.sku
    except:
        sku = ''

    """ product_name """
    try:
        product_name = obj.productName
    except:
        product_name = ''

    """ product_category """
    try:
        product_category = obj.product_category
    except:
        product_category = ''

    """ counter """
    try:
        counter = {"id": obj.counter.id, "name": obj.counter.name}
    except:
        counter = None

    """ unit_cost """
    try:
        unit_cost = obj.stock.price_override.gross
    except:
        unit_cost = obj.unit_price

    """ quantity """
    try:
        quantity = CounterItems.objects.instance_quantities(obj.stock, filter_type='stock', counter=obj.counter)
    except:
        quantity = 0

    """ tax """
    try:
        tax = obj.tax
    except:
        tax = 0

    """ discount """
    try:
        discount = obj.discount
    except:
        discount = 0

    try:
        attributes_list = ProductVariant.objects.filter(pk=obj.stock.variant.pk).extra(select=dict(key="content_item.data -> 'attributes'")) \
            .values('attributes').order_by('attributes')
    except Exception as ex:
        print (ex)
        attributes_list = {}

    try:
        discounts = []
        all_discounts = Sale.objects.filter(variant__pk=obj.stock.variant.pk)
        print(obj.stock.variant.pk)
        for disc in all_discounts:
            try:
                dis = {}
                dis['id'] = disc.id
                dis['name'] = disc.name
                dis['quantity'] = disc.quantity
                dis['price'] = disc.value
                dis['start_time'] = disc.start_time
                dis['end_time'] = disc.end_time
                dis['start_date'] = disc.start_date
                dis['end_date'] = disc.end_date
                dis['date'] = disc.date
                dis['day'] = disc.day
                discounts.append(dis)
            except Exception as e:
                logger.info('Error in assigning discounts: ' + str(e))
    except Exception as e:
        logger.info('Error in assigning discounts: ' + str(e))
        discounts = []

    json_data = {
        "id": id,
        "sku": sku,
        "quantity": quantity,
        "product_name": product_name,
        "product_category": product_category,
        "unit_cost": unit_cost,
        "tax": tax,
        "discount": discount,
        "counter": counter,
        "kitchen": None,
        "attributes_list": attributes_list,
        "discounts": discounts
    }

    return json_data


""" set the menu items json """


def getMenuItemsJsonData(obj):
    """ id """
    id = obj.id

    """ sku """
    try:
        sku = obj.menu.id
    except:
        sku = ''

    """ product_name """
    try:
        product_name = obj.name
    except:
        product_name = ''

    """ product_category """
    try:
        product_category = obj.menu.category.name
    except:
        product_category = ''

    """ kitchen """
    try:
        kitchen = {"id": obj.counter.id, "name": obj.counter.name}
    except:
        kitchen = None

    """ unit_cost """
    try:
        unit_cost = obj.price
    except:
        unit_cost = 0

    """ quantity """
    try:
        quantity = obj.qty
    except:
        quantity = 0

    try:
        attributes_list = ProductVariant.objects.filter(pk=obj.stock.variant.pk).extra(select=dict(key="content_item.data -> 'attributes'")) \
            .values('attributes').order_by('attributes')
    except:
        attributes_list = {}

    discounts = []

    """ tax """
    tax = 0

    """ discount """
    discount = 0

    json_data = {
        "id": id,
        "sku": sku,
        "quantity": quantity,
        "product_name": product_name,
        "product_category": product_category,
        "unit_cost": unit_cost,
        "tax": tax,
        "discount": discount,
        "kitchen": kitchen,
        "counter": None,
        "attributes_list": attributes_list,
        "discounts": discounts
    }

    return json_data
