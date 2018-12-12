from django.conf.urls import url

from .views import (
    SaleListAPIView,
    SaleCreateAPIView,
    SaleDetailAPIView,
    ListAPIView,
    ListItemAPIView,

    ItemListAPIView,
    SoldItemListAPIView,
    SaleMarginListAPIView,
    UserSaleAPIView
    )


urlpatterns = [
    url(r'^$', SaleListAPIView.as_view(), name='detail'),
    url(r'^create-sale/$', SaleCreateAPIView.as_view(), name='create-sale'),
    url(r'^list/(?P<pk>[0-9]+)/$', SaleDetailAPIView.as_view(), name='api-list-sale'),
    url(r'^list/item/(?P<pk>[0-9]+)/$', ListItemAPIView.as_view(), name='api-list-sale'),
    url(r'^list/$', ListAPIView.as_view(), name='api-list'),

    url(r'^totals/$', SoldItemListAPIView.as_view(),
        name='list-sales'),
    url(r'^user/totals/$', UserSaleAPIView.as_view(),
        name='user-sales'),
    url(r'^margin/', SaleMarginListAPIView.as_view(),
        name='sale-margin'),
    url(r'^items/(?P<pk>[0-9]+)/$', ItemListAPIView.as_view(),
        name='list-sold-items'),
]

