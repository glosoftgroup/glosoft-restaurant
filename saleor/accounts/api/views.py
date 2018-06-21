import logging
from rest_framework import generics
from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from .pagination import PostLimitOffsetPagination
from saleor.accounts.models import PettyCash, Expenses
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from .serializers import (
    PettyCashListSerializer,
    PettyCashDetailSerializer,
    PettyCashXSerializer
)
from django.views.generic import TemplateView, DetailView

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
factory = APIRequestFactory()
request = factory.get('/')
serializer_context = {
    'request': Request(request),
}


class PettyCashListAPIView(generics.ListAPIView):
    serializer_class = PettyCashListSerializer
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = PettyCash.objects.all()

        date = self.request.GET.get('date')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        mode = self.request.GET.get('mode')
        page_size = self.request.GET.get('page_size')

        if page_size:
            pagination.PageNumberPagination.page_size = page_size
        else:
            pagination.PageNumberPagination.page_size = 10

        if date:
            if mode:
                year = date.split("-")[0]
                if len(date.split('-')) >= 2:
                    month = date.split("-")[1]
                else:
                    month = "01"
                if mode == "month":
                    queryset_list = queryset_list.filter(created__year=year,
                                                         created__month=month)
                elif mode == "year":
                    queryset_list = queryset_list.filter(created__year=year)
                else:
                    queryset_list = queryset_list.filter(created__icontains=date)
            else:
                queryset_list = queryset_list.filter(created__icontains=date)

        elif date_from and date_to:
            if mode:
                year_from = date_from.split("-")[0]
                if len(date_from.split('-')) >= 2:
                    month_from = date_from.split("-")[1]
                else:
                    month_from = "01"

                year_to = date_to.split("-")[0]
                if len(date_to.split('-')) >= 2:
                    month_to = date_to.split("-")[1]
                else:
                    month_to = "01"

                if mode == "month":
                    queryset_list = queryset_list.filter(created__year__gte=year_from,
                                                         created__month__gte=month_from,
                                                         created__year__lte=year_to,
                                                         created__month__lte=month_to)
                elif mode == "year":
                    queryset_list = queryset_list.filter(created__year__gte=year_from,
                                                         created__year__lte=year_to)
                else:
                    queryset_list = queryset_list.filter(created__range=[date_from, date_to])
            else:
                queryset_list = queryset_list.filter(created__range=[date_from, date_to])

        return queryset_list


class PettyCashCompareAPIViewz(APIView):
    queryset = PettyCash.objects.all()
    serializer_class = PettyCashDetailSerializer(instance=queryset, context=serializer_context)

    def get_queryset(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        # Note the use of `get_queryset()` instead of `self.queryset`
        query = self.request.GET.get('q')
        queryset = self.get_queryset().filter(pk=pk)
        serializer = PettyCashDetailSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)


class PettyCashDetailView(DetailView):
    model = PettyCash
    context_object_name = 'pettycash'
    template_name = "petty_cash/detail.html"

    def get_context_data(self, **kwargs):
        context = super(PettyCashDetailView, self).get_context_data(**kwargs)

        context['pcash'] = PettyCash.objects.filter(pk=self.kwargs.get('pk'))

        date = PettyCash.objects.get(pk=self.kwargs.get('pk')).created.date().strftime('%Y-%m-%d')

        expenses = Expenses.objects.filter(added_on__icontains=date)
        if expenses:
            context['expenses'] = expenses
            context['total_expenses'] = expenses.aggregate(Sum('amount'))['amount__sum']
        else:
            context['expenses'] = []
            context['total_expenses'] = 0

        return context


class PettyCashCompareAPIView(APIView):
    def get(self, request):
        query = self.request.GET.get('q', '')

        data = []
        json_data = {
            'pdate': "2018-10-12",
            'opening_cash': "wer",
            'cash_added': "qwe",
            'closing_amount': "oosd",
            'balance': "werwe",
            'expenses_incurred': "werf",
            'expenses': {}
        }

        data.append(json_data)

        serializer = PettyCashXSerializer(data, many=True)
        return Response(serializer.data)
