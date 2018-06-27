from rest_framework_jwt.views import obtain_jwt_token
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.views import serve
from django.views.i18n import javascript_catalog
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from .accounts.urls import urlpatterns as accounts_urls
from .api.booking.urls import urlpatterns as api_booking_urls
from .api.cash.urls import urlpatterns as api_cash_urls
from .api.category.urls import urlpatterns as api_category_urls
from .api.customer.urls import urlpatterns as api_customer_urls
from .api.discount.urls import urlpatterns as api_discount_urls
from .api.invoice.urls import urlpatterns as api_invoice_urls
from .api.credit.urls import urlpatterns as api_credit_urls
from .api.notification.urls import urlpatterns as api_notification_urls
from .api.order.urls import urlpatterns as api_order_urls
from .api.order_number.urls import urlpatterns as api_order_number_urls
from .api.payment.urls import urlpatterns as api_payment_urls
from .api.product.urls import urlpatterns as api_urls
from .api.property.urls import urlpatterns as api_property_urls
from .api.purchase.urls import urlpatterns as api_purchase_urls
from .api.purchase_variant.urls import urlpatterns as api_purchase_variant_urls
from .api.stock.urls import urlpatterns as api_stock_urls
from .api.room.urls import urlpatterns as api_maintenance_urls
from .api.sale.urls import urlpatterns as api_sale_urls
from .api.salepoint.urls import urlpatterns as api_salepoint_urls
from .api.settings.urls import urlpatterns as api_settings_urls
from .api.sms.urls import urlpatterns as api_sms_urls
from .api.table.urls import urlpatterns as api_table_urls
from .api.terminal.urls import urlpatterns as api_terminal_urls
from .api.variant.urls import urlpatterns as api_variant_urls
from .cart.urls import urlpatterns as cart_urls
from .checkout.urls import urlpatterns as checkout_urls
from .core.sitemaps import sitemaps
from .core.urls import urlpatterns as core_urls
from .dashboard.urls import urlpatterns as dashboard_urls
from .data_feeds.urls import urlpatterns as feed_urls
from .order.urls import urlpatterns as order_urls
from .payment.urls import urlpatterns as payment_urls
from .product.urls import urlpatterns as product_urls
from .registration.urls import urlpatterns as registration_urls
from .search.urls import urlpatterns as search_urls
from .userprofile.urls import urlpatterns as userprofile_urls
from .salepoints.urls import urlpatterns as salepoints_urls
from .wing.urls import urlpatterns as wing_urls
from .propertytype.urls import urlpatterns as propertytype_urls
from .section.urls import urlpatterns as section_urls
from .menucategory.urls import urlpatterns as menu_categories_urls
from .table.urls import urlpatterns as menu_table_urls
from .menu.urls import urlpatterns as menu_urls
from .kitchen.urls import urlpatterns as kitchen_urls
from .counter.urls import urlpatterns as counter_urls
from .kitchentransfer.urls import urlpatterns as kitchentransfer_urls
from .countertransfer.urls import urlpatterns as countertransfer_urls
from .counter_transfer_report.urls import urlpatterns as counter_transfer_report_urls
from .kitchen_transfer_report.urls import urlpatterns as kitchen_transfer_report_urls
from .menutransfer.urls import urlpatterns as menutransfer_urls
from .return_sale.urls import urlpatterns as return_sale_urls
from .return_purchase.urls import urlpatterns as return_purchase_urls
import notifications.urls
from .api.login import ObtainJSONWebToken
from . import decorators


urlpatterns = [
    url(r'^', include(core_urls)),
    url(r'^account/', include(registration_urls)),
    url(r'^accounts/', include(accounts_urls, namespace='accounts')),
    url(r'^api/cash/', include(api_cash_urls, namespace='cash-api')),
    url(r'^api/booking/', include(api_booking_urls, namespace='booking-api')),
    url(r'^api/customer/', include(api_customer_urls, namespace='customer-api')),
    url(r'^api/category/', include(api_category_urls, namespace='category-api')),
    url(r'^api/credit/', include(api_credit_urls, namespace='credit-api')),
    url(r'^api/discount/', include(api_discount_urls, namespace='discount-api')),
    url(r'^api/invoice/', include(api_invoice_urls, namespace='invoice-api')),
    url(r'^api/notification/', include(api_notification_urls, namespace='notification-api')),
    url(r'^api/order/', include(api_order_urls, namespace='order-api')),
    url(r'^api/order/number', include(api_order_number_urls, namespace='order-number-api')),
    url(r'^api/products/', include(api_urls, namespace='product-api')),
    url(r'^api/property/', include(api_property_urls, namespace='property-api')),
    url(r'^api/payment/', include(api_payment_urls, namespace='payment-api')),
    url(r'^api/purchase/', include(api_purchase_urls, namespace='purchase-api')),
    url(r'^api/purchase/variant', include(api_purchase_variant_urls, namespace='purchase-variant-api')),
    url(r'^api/stock/', include(api_stock_urls, namespace='api-stock')),
    url(r'^api/maintenance/', include(api_maintenance_urls, namespace='maintenance-api')),
    url(r'^api/sale/', include(api_sale_urls, namespace='sale-api')),
    url(r'^api/setting/', include(api_settings_urls, namespace='setting-api')),
    url(r'^api/sale-point/', include(api_salepoint_urls, namespace='sale_point-api')),
    url(r'^api/sms/', include(api_sms_urls, namespace='sms-api')),
    url(r'^api/table/', include(api_table_urls, namespace='table-api')),
    url(r'^api/terminal/', include(api_terminal_urls, namespace='terminal-api')),
    url(r'^api/variant/', include(api_variant_urls, namespace='variant-api')),
    url(r'^cart/', include(cart_urls, namespace='cart')),
    url(r'^checkout/', include(checkout_urls, namespace='checkout')),
    url(r'^dashboard/', include(dashboard_urls, namespace='dashboard')),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG))),
    url(r'^jsi18n/$', javascript_catalog, name='javascript-catalog'),
    url(r'^notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^order/', include(order_urls, namespace='order')),
    url(r'^payment/', include(payment_urls, namespace='payment')),
    url(r'^products/', include(product_urls, namespace='product')),
    url(r'^profile/', include(userprofile_urls, namespace='profile')),
    url(r'^search/', include(search_urls, namespace='search')),
    url(r'^feeds/', include(feed_urls, namespace='data_feeds')),
    url(r'^propertytype/', include(propertytype_urls, namespace="propertytype")),
    url(r'^wing/', include(wing_urls, namespace='wing')),
    url(r'^section/', include(section_urls, namespace='section')),
    url(r'^menucategory/', include(menu_categories_urls, namespace='menucategory')),
    url(r'^table/', include(menu_table_urls, namespace='table')),
    url(r'^menu/', include(menu_urls, namespace='menu')),
    url(r'^kitchen/', include(kitchen_urls, namespace='kitchen')),
    url(r'^counter/', include(counter_urls, namespace='counter')),
    url(r'^counter/transfer/', include(countertransfer_urls, namespace='countertransfer')),
    url(r'^counter/transfer/report/', include(counter_transfer_report_urls, namespace='counter_transfer_report')),
    url(r'^kitchen/transfer/report/', include(kitchen_transfer_report_urls, namespace='kitchen_transfer_report')),
    url(r'^kitchen/transfer/', include(kitchentransfer_urls, namespace='kitchentransfer')),
    url(r'^menu/transfer/', include(menutransfer_urls, namespace='menutransfer')),
    url(r'^return/sale/', include(return_sale_urls, namespace='return_sale')),
    url(r'^return/purchase/', include(return_purchase_urls, namespace='return_purchase')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^sale/points/', include(salepoints_urls, namespace='salepoints')),
    url(r'', include('payments.urls')),
    url('', include('social_django.urls', namespace='social')),
    #jwt post token code url
    # url(r'^api/auth/token/', obtain_jwt_token),
    url(r'^api/auth/token/', ObtainJSONWebToken.as_view()),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve)
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
