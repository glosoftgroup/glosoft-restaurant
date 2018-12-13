from django.conf.urls import url

from .views import ListAPIView, ListWaitersAPIView


urlpatterns = [
    url(r'^$', ListAPIView.as_view(), name='users'),
    url(r'^waiter/$', ListWaitersAPIView.as_view(), name='waiters'),
]

