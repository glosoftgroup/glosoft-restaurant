from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from rest_framework import serializers
from .pagination import PostLimitOffsetPagination

from saleor.countertransfer.models import CounterTransfer as Table
from saleor.product.models import Stock
from .serializers import (
    CreateListSerializer,
    TableListSerializer,
    UpdateSerializer
     )

User = get_user_model()


class CreateAPIView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = CreateListSerializer

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class DestroyView(generics.DestroyAPIView):
    queryset = Table.objects.all()

    def perform_destroy(self, instance):
        items = instance.counter_transfer_items.all()
        for item in items:
            Stock.objects.increase_stock(item.stock, item.qty)
        # raise serializers.ValidationError('You cannot delete ')
        instance.delete()


class ListAPIView(generics.ListAPIView):
    """
        list details
        GET /api/setting/
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
                queryset_list = Table.objects.filter(customer__pk=self.kwargs['pk']).order_by('car').distinct('car').select_related()
            else:
                queryset_list = Table.objects.all.select_related()
        except Exception as e:
            queryset_list = Table.objects.all()

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(counter__name__icontains=query))
        return queryset_list.order_by('-id')


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
