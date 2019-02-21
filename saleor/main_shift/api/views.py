from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination
from saleor.main_shift.models import MainShift as Table
from .serializers import (
    TableListSerializer,
    UpdateSerializer
     )

User = get_user_model()


class ListAPIView(generics.ListAPIView):

    serializer_class = TableListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):

        queryset_list = Table.objects.all()

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        if self.request.GET.get('date'):
            query_date = self.request.GET.get('date')
            queryset_list = queryset_list.filter(
                Q(opening_time__icontains=query_date) |
                Q(closing_time__icontains=query_date))
        return queryset_list.order_by('-id')


class UpdateAPIView(generics.RetrieveUpdateAPIView):

    queryset = Table.objects.all()
    serializer_class = UpdateSerializer
