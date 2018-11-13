from django.db.models import Q, F
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination
from ...sale.models import Sales
from ...sale.models import SoldItem as Item
from .serializers import (
    ListSaleSerializer,
    CreateSaleSerializer,
    ItemSerializer
)

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
