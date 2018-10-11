from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination

from saleor.mpesa_transactions.models import MpesaTransactions, MpesaTransactionsTest
from .serializers import (
    TableListSerializer,
    UpdateSerializer
     )

User = get_user_model()
Table = MpesaTransactions


class UpdateAPIView(generics.RetrieveUpdateAPIView):
    """
        update instance details
        @:param pk house id
        @:method PUT

        PUT /api/house/update/
        payload Json: /payload/settings.json
    """
    queryset = Table.objects.all()
    serializer_class = UpdateSerializer


""" TODO: delete this functionality after completion of implementation """

from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class TestListAPIView(generics.ListAPIView):

    serializer_class = TableListSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = MpesaTransactionsTest.objects.filter(pk=self.kwargs['pk'])
            else:
                queryset_list = MpesaTransactionsTest.objects.filter()
        except Exception as e:
            queryset_list = MpesaTransactionsTest.objects.all()

        if self.request.GET.get('is_picked_status') and self.request.GET.get('is_picked_status').lower() == 'true':
            is_picked_status = True
        else:
            is_picked_status = False

        if self.request.GET.get('status'):
            try:
                status = int(self.request.GET.get('status'))
            except (ValueError, Exception) as e:
                status = 0
        else:
            status = 0

        queryset_list = queryset_list.filter(is_picked_status=is_picked_status, status=status)

        page_size = 'page_size'

        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query))
        return queryset_list.order_by('-id')
