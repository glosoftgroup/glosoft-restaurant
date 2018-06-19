import datetime
import logging
from datetime import timedelta
from django.utils.dateformat import DateFormat
from rest_framework import generics
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from .pagination import PostLimitOffsetPagination
from saleor.accounts.models import PettyCash, Expenses
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    PettyCashListSerializer,
    NewPettyCashListSerializer,
)

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


class ListAPIView(APIView):
    def get(self, request):

        query = self.request.GET.get('q', '')

        date = request.GET.get('date')
        date_from = request.GET.get('from')
        date_to = request.GET.get('to')

        try:
            if date:
                date = date
            else:
                date = DateFormat(datetime.datetime.today()).format('Y-m-d')

            pettyCash = dateFactorial(date)
            lastEntry = pettyCash.latest('id')

            pd = DateFormat(lastEntry.created).format('Y-m-d')
            td = DateFormat(datetime.datetime.today()).format('Y-m-d')
            if td == pd:
                dateToday = 1
                expenses = Expenses.objects.filter(added_on__icontains=pd).aggregate(Sum('amount'))['amount__sum']
                added = lastEntry.added
                opening = lastEntry.opening
            else:
                dateToday = 0
                try:
                    expenses = Expenses.objects.filter(added_on__icontains=date).aggregate(Sum('amount'))['amount__sum']
                    if expenses:
                        added = lastEntry.added
                        opening = lastEntry.opening
                    else:
                        expenses = 0
                        added = 0
                        opening = lastEntry.closing
                except:
                    expenses = 0

            date = DateFormat(datetime.datetime.strptime(date, '%Y-%m-%d')).format('jS F Y')
            amount = lastEntry.closing
            opening = opening
            added = added
            closing = lastEntry.closing

        except BaseException, e:
            info_logger.info('Error in getting petty cash amount: ' + str(e))
            dateToday = 0
            date = datetime.date.today()
            amount = 0
            opening = 0
            added = 0
            closing = 0
            expenses = 0

        data = []
        json_data = {
            # 'pdate': date,
            # 'opening_amount': opening,
            # 'added_amount': added,
            # 'closing_amount': closing,
            # 'amount': amount,
            # 'dateToday': dateToday,
            # 'expenses': expenses,

            'pdate': date,
            'opening_cash': opening,
            'cash_added': added,
            'closing_amount': closing,
            'balance': amount,
            'expenses_incurred': expenses,
            'expenses': {}
        }

        data.append(json_data)

        serializer = PettyCashListSerializer(data, many=True)
        return Response(serializer.data)


def dateFactorial(date=None, date_from=None, date_to=None):
    date = str(date)
    enteredDate = DateFormat(datetime.datetime.strptime(date, '%Y-%m-%d')).format('Y-m-d')
    firstDateEntry = DateFormat(PettyCash.objects.all().first().created).format('Y-m-d')
    if enteredDate < firstDateEntry:
        raise BaseException
    elif enteredDate == firstDateEntry:
        return PettyCash.objects.filter(created__icontains=firstDateEntry)
    elif date_from and date_to:
        return PettyCash.objects.filter(created__range=[date_from, date_to])
    else:
        try:
            query = PettyCash.objects.filter(created__icontains=enteredDate)
            if query.exists():
                return query
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            return dateFactorial(
                DateFormat(datetime.datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).format('Y-m-d'))


class PettyCashListAPIView(generics.ListAPIView):
    serializer_class = NewPettyCashListSerializer
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
                month = date.split("-")[1]
                if mode and mode == "month":
                    queryset_list = queryset_list.filter(created__year=year,
                                                         created__month=month)
                elif mode and mode == "year":
                    queryset_list = queryset_list.filter(created__year=year)
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
                month_to = date_to.split("-")[1]
                if mode and mode == "month":
                    queryset_list = queryset_list.filter(created__year__gte=year_from,
                                                         created__month__gte=month_from,
                                                         created__year__lte=year_to,
                                                         created__month__lte=month_to)
                elif mode and mode == "year":
                    queryset_list = queryset_list.filter(created__year__gte=year_from,
                                                         created__year__lte=year_to)
            else:
                queryset_list = queryset_list.filter(created__range=[date_from, date_to])


        return queryset_list
