from django.conf.urls import url

from .views import (
    start_shift,
    end_shift
    )


urlpatterns = [
    url(r'^$', start_shift, name='api-start-shift'),
    url(r'^end/$', end_shift, name='api-end-shift'),
]

