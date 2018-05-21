from django.conf.urls import url

from .views import (
    CategoryListAPIView,
    BusinessTypeCategoryListAPIView,
    )


urlpatterns = [
    url(r'^$', CategoryListAPIView.as_view(), name='api-category-list'),
    url(r'^business-type/(?P<pk>[0-9]+)/$',
        BusinessTypeCategoryListAPIView.as_view(),
        name='api-business_type-categories'),
]

