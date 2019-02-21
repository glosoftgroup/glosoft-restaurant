from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from .api.views import *
from .models import MainShift as Table


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="main_shift/list.html"), name="index"),
    url(r'^api/list/$', ListAPIView.as_view(), name='api-list'),

    url(r'^api/update/(?P<pk>[0-9]+)/$', UpdateAPIView.as_view(), name='api-update'),
    url(r'^add/$', TemplateView.as_view(template_name="main_shift/form.html"), name='add'),
    url(r'^update/(?P<pk>[0-9]+)/$',
        UpdateView.as_view(
            template_name="main_shift/form.html", model=Table,
            fields=[
                'id', 'user', 'start_time',
                'start_counter_balance', 'start_note',
                'end_time', 'end_counter_balance', 'end_note']),
        name='update')
]

