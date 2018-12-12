from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .api.views import *
from .models import VisaTransactions as Table


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="visa_transactions/list.html"), name="index"),
    url(r'^api/list/$', ListAPIView.as_view(), name='api-list'),
    url(r'^api/list/detail/$', ListSingleAPIView.as_view(), name='api-list-detail'),
    url(r'^api/create/$', CreateAPIView.as_view(), name='api-create-mpesa-payment'),
    url(r'^add/$', TemplateView.as_view(template_name="visa_transactions/form.html"), name='add'),
    url(r'^update/(?P<pk>[0-9]+)/$', UpdateView.as_view(template_name="visa_transactions/form.html", model=Table, fields=['id', 'name']),
        name='update'),
    url(r'^api/detail/(?P<pk>[0-9]+)/$', DetailAPIView.as_view(),
        name='api-mpesa-detail'),
]

