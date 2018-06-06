# category rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...product.models import Category, ProductVariant
from saleor.menucategory.models import MenuCategory
from saleor.menu.models import Menu
from saleor.section.models import Section
from rest_framework.serializers import (
                HyperlinkedIdentityField,
                SerializerMethodField,
                )
User = get_user_model()


class CategoryListSerializer(serializers.ModelSerializer):
    product_variants_url = HyperlinkedIdentityField(view_name='countertransfer:api-list-category')
    total_products = SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id',
                  'name',
                  'description',
                  'section',
                  'product_variants_url',
                  'total_products',)

    def get_total_products(self, obj):
        return len(ProductVariant.objects.filter(product__categories__pk=obj.pk))


class MenuCategoryListSerializer(serializers.ModelSerializer):
    product_variants_url = HyperlinkedIdentityField(view_name='menutransfer:api-list-category')
    section = SerializerMethodField()
    total_products = SerializerMethodField()
    description = SerializerMethodField()

    class Meta:
        model = MenuCategory
        fields = ('id',
                  'name',
                  'description',
                  'section',
                  'product_variants_url',
                  'total_products',)

    def get_total_products(self, obj):
        try:
            return Menu.objects.filter(category__pk=obj.pk).count()
        except Exception as e:
            return 0

    def get_description(self, obj):
        return ''

    def get_section(self, obj):
        try:
            return Section.objects.get(name="Restaurant").pk
        except Exception as e:
            return None