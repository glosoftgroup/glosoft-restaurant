from django.conf.urls import url

from .views import (
    new_code,
    )


urlpatterns = [
    url(r'^$', new_code, name='api-code_number'),
]

