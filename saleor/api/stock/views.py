from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination

from saleor.product.models import Stock as Table
from .serializers import (
    CreateListSerializer,
    TableListSerializer,
    UpdateSerializer
     )

User = get_user_model()


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
