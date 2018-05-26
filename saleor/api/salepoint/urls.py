from django.conf.urls import url

from .views import (
    SalePointListAPIView,
    CountersAndKitchensListAPIView
    )


urlpatterns = [
    url(r'^$', SalePointListAPIView.as_view(), name='api-sale_point-list'),
    url(r'^points/$', CountersAndKitchensListAPIView.as_view(), name='api-counters-kitchens-list'),
]

