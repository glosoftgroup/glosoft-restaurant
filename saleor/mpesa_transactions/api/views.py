from rest_framework import generics
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination
from saleor.mpesa_transactions.models import MpesaTransactions
from .serializers import TableListSerializer, CreatePaymentSerializer, DetailSerializer
from structlog import get_logger

logger = get_logger(__name__)

Table = MpesaTransactions


class ListAPIView(generics.ListAPIView):
    """
        list details
    """
    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = Table.objects.filter(pk=self.kwargs['pk'])
            else:
                queryset_list = Table.objects.all()
        except Exception as e:
            queryset_list = Table.objects.all()

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created_at__icontains=self.request.GET.get('date'))

        if self.request.GET.get('status'):
            try:
                status = int(self.request.GET.get('status'))
                queryset_list = queryset_list.filter(status=status)
            except Exception as e:
                logger.error('Error converting string to int ' + str(e))

        if self.request.GET.get('client_status'):
            try:
                client_status = int(self.request.GET.get('client_status'))
                queryset_list = queryset_list.filter(client_status=client_status)
            except Exception as e:
                logger.error('Error converting string to int ' + str(e))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(msisdn__icontains=query) |
                Q(trans_id__icontains=query) |
                Q(first_name__icontains=query) |
                Q(middle_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(invoice_number__icontains=query) |
                Q(business_short_code__icontains=query) |
                Q(transaction_type__icontains=query) |
                Q(created_at__icontains=query))
        return queryset_list.order_by('-id')


class ListSingleAPIView(generics.RetrieveAPIView):
    """
        list details
    """
    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = MpesaTransactions.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.last()

        if self.request.GET.get('msisdn'):
            try:
                msisdn = self.request.GET.get('msisdn')
                obj = queryset.filter(msisdn=msisdn).last()
            except Exception as e:
                logger.error('Error getting the last offline mpesa payment ' + str(e))
        return obj


class CreateAPIView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = CreatePaymentSerializer


class DetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = MpesaTransactions.objects.all()
    serializer_class = DetailSerializer
