from django.db.models import Q
from rest_framework import pagination
from rest_framework import generics
from django.contrib.auth import get_user_model

from .pagination import CustomPagination
from .serializers import (
    CustomerListSerializer,
    CreditWorthyCustomerSerializer,
    CustomerUpdateSerializer,
    PaymentListSerializer
)

from ...customer.models import Customer as Table
from ...booking.models import RentPayment
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


class CreditWorthyCustomerListAPIView(generics.ListAPIView):
    serializer_class = CreditWorthyCustomerSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.filter(creditable=True)
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)
            ).distinct()
        return queryset_list


class CustomerListAPIView(generics.ListAPIView):
    serializer_class = CustomerListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query) |
                Q(mobile__icontains=query)
            ).distinct()
        return queryset_list


class CustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = CustomerListSerializer


class CustomerUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Table.objects.all()
    serializer_class = CustomerUpdateSerializer


class CustomerPagListAPIView(generics.ListAPIView):
    serializer_class = CustomerListSerializer
    pagination_class = CustomPagination
    queryset = Table.objects.all()

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date_joined__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query) |
                Q(mobile__icontains=query) |
                Q(email__icontains=query)
            ).distinct()
        return queryset_list


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    pagination_class = CustomPagination
    queryset = RentPayment.objects.all()

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset = RentPayment.objects.filter(customer__pk=self.kwargs['pk'])
            else:
                queryset = RentPayment.objects.all()
        except Exception as e:
            queryset = RentPayment.objects.all().select_related()

        queryset_list = RentPayment.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset = queryset.filter(date_paid__icontains=self.request.GET.get('date'))
        if query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query) |
                Q(room__name__icontains=query)
            )
        return queryset

    def filter_queryset(self, queryset):
        queryset = super(PaymentListAPIView, self).filter_queryset(queryset)
        return queryset.order_by('-id')
