from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^$', ListAPIView.as_view(), name='api-stock-list'),
]

