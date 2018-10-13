from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination

from saleor.mpesa_transactions.models import MpesaTransactionsTest
from .serializers import TableListSerializer, UpdateSerializer



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

        queryset_list = MpesaTransactionsTest.objects.all()

        if self.request.GET.get('status'):
            try:
                picked_status = int(self.request.GET.get('status'))
            except (ValueError, Exception) as e:
                picked_status = 0
        else:
            picked_status = 0

        queryset_list = queryset_list.filter(status=picked_status)

        page_size = 'page_size'

        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        """ if queryset exists then update the status field of all records """

        if queryset_list.exists():

            q_ids = [i.id for i in queryset_list]
            """ update the status of all the records """
            queryset_list.update(status=1)
            """ filter the new queryset since it has changed during the update """
            queryset_list = MpesaTransactionsTest.objects.filter(pk__in=[i for i in q_ids])

        return queryset_list.order_by('-id')


@api_view(['GET', 'POST'])
def change_transactions_status(request):
    if request.method == 'POST':
        return Response({'message': 'success'}, status=status.HTTP_200_OK)
    elif request.method == 'GET':
        queryset = MpesaTransactionsTest.objects.all()

        if request.GET.get('status'):
            try:
                picked_status = int(request.GET.get('status'))
            except (ValueError, Exception) as e:
                picked_status = 0
        else:
            picked_status = 0

        queryset = queryset.filter(status=picked_status)

        if queryset.exists():
            ql = [i.id for i in queryset]
            queryset.update(status=1)
            queryset = MpesaTransactionsTest.objects.filter(pk__in=[i for i in ql])

        serializer = TableListSerializer(queryset, many=True)
        return Response(serializer.data)
