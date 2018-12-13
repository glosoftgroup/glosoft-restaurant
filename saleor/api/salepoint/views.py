from ...salepoints.models import SalePoint
from saleor.counter.models import Counter
from saleor.kitchen.models import Kitchen
from .serializers import (
    SalePointListSerializer,
    CountersAndKitchensSerializer,
     )
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()

class SalePointListAPIView(generics.ListAPIView):
    serializer_class = SalePointListSerializer
    queryset = SalePoint.objects.all()

class CustomSalePointListAPIView(generics.ListAPIView):
    serializer_class = SalePointListSerializer
    queryset = SalePoint.objects.all()

class CountersAndKitchensListAPIView(views.APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get(self, request):
    	points = []
    	for counter in Counter.objects.all():
    		setattr(counter, "point", "counter")
    		points.append(counter)

    	for kitchen in Kitchen.objects.all():
    		setattr(kitchen, "point", "kitchen")
    		points.append(kitchen)

        results = CountersAndKitchensSerializer(points, many=True).data
        return Response(results)