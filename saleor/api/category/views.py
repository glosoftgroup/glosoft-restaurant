from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import get_user_model

from .serializers import (
    CategoryListSerializer,
    MenuCategoryListSerializer
     )
from ...product.models import Category
from saleor.menucategory.models import MenuCategory

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

    """ choose the default serializer class based on the name """
    def get_serializer_class(self):
        if self.kwargs["name"].lower() == "restaurant": # here add the logic to decide the asset type
             return MenuCategoryListSerializer
        return CategoryListSerializer

    """ choose the default queryset based on the name """
    def get_queryset(self):
        if self.kwargs["name"].lower() == "restaurant":  # here add the logic to decide the asset type
            return MenuCategory.objects.all()
        return Category.objects.all()

    def list(self, request, pk=None, name=None):
        serializer_context = {
            'request': Request(request),
        }
        if pk:
            queryset = self.get_queryset().filter(section__name=name)
            serializer = CategoryListSerializer(queryset, context=serializer_context, many=True)
        if name:
            if name.lower() == "bar":
                queryset = self.get_queryset().filter(section__name__icontains=name)
                serializer = CategoryListSerializer(queryset, context=serializer_context, many=True)
            elif name.lower() == "restaurant":
                serializer = MenuCategoryListSerializer(self.get_queryset(), context=serializer_context, many=True)

        return Response(serializer.data)

