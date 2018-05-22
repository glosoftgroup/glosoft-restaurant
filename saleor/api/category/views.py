from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import get_user_model

from .serializers import (
    CategoryListSerializer,
     )
from ...product.models import Category

User = get_user_model()


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()


class BusinessTypeCategoryListAPIView(generics.ListAPIView):
    """
    Business type categories (Bar or Kitchen(restaurant categories)
    :param pk integer, business type id

    payload: /payload/businesstype-categories.json
    """
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(section__pk=pk)
        serializer = CategoryListSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

