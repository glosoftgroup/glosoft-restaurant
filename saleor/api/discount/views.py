from .serializers import (
    DiscountListSerializer,
    CustomerDiscountListSerializer,
)
from rest_framework import generics
from django.contrib.auth import get_user_model
from ...discount.models import Sale
from ...customer.models import Customer

User = get_user_model()


class DiscountListAPIView(generics.ListAPIView):
    serializer_class = DiscountListSerializer
    queryset = Sale.objects.all()


class CustomerDiscountListAPIView(generics.RetrieveAPIView):
    serializer_class = CustomerDiscountListSerializer
    queryset = Customer.objects.all()
