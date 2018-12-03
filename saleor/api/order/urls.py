from django.conf.urls import url

from .views import (
    DestroyView,
    OrderCreateAPIView,
    OrderItemsListAPIView,
    OrderListAPIView,
    OrderStatusListAPIView,
    OrderUpdateAPIView,
    OrderReadyOrCollectedAPIView,
    RoomOrdersListAPIView,
    SalePointNextOrdersListAPIView,
    SalePointOrdersItemListAPIView,
    SalePointOrdersListAPIView,
    SearchOrdersListAPIView,
    TableOrdersListAPIView,
    CancelledOrderListAPIView
    )


urlpatterns = [
    url(r'^$', OrderListAPIView.as_view(), name='list-orders'),
    url(r'^items/$', OrderItemsListAPIView.as_view(), name='list-ordered-items'),
    url(r'^create-order/$', OrderCreateAPIView.as_view(), name='create-order'),
    url(r'^delete/(?P<pk>[0-9]+)$', DestroyView.as_view(), name='delete-order'),
    url(r'^search/status/$', OrderStatusListAPIView.as_view(), name='search-orders'),
    url(r'^sale-point/(?P<pk>[0-9]+)$', SalePointOrdersListAPIView.as_view(),
        name='api-sale_point-orders'),
    url(r'^sale-point/(?P<pk>[0-9]+)/(?P<order_pk>[0-9]+)$', SalePointNextOrdersListAPIView.as_view(),
        name='api-sale_point-next-orders'),
    url(r'^sale-point-items/(?P<pk>[0-9]+)$', SalePointOrdersItemListAPIView.as_view(),
        name='api-sale_point-orders-items'),
    url(r'^table/(?P<pk>[0-9]+)$', TableOrdersListAPIView.as_view(),
        name='api-table-orders'),
    url(r'^search/orders/$', SearchOrdersListAPIView.as_view(),
        name='api-restaurant-orders'),
    url(r'^room/(?P<pk>[0-9]+)$', RoomOrdersListAPIView.as_view(),
        name='api-room-orders'),
    url(r'^update-order/(?P<pk>[0-9]+)/$', OrderUpdateAPIView.as_view(),
        name='update-order'),
    url(r'^ready/collect/order/(?P<pk>[0-9]+)/$', OrderReadyOrCollectedAPIView.as_view(),
        name='ready-collect-order'),
    url(r'^cancelled/$', CancelledOrderListAPIView.as_view(), name='cancelled-orders'),
]

