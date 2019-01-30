from django.db.models.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password
from django.conf import settings
from ..sale.models import PaymentOption, Terminal
from ..product.models import StockLocation
from saleor.salepoints.models import SalePoint
from saleor.section.models import Section
from saleor.supplier.models import Supplier
from saleor.userprofile.models import User
from saleor.payment.models import PaymentOption as Payment
from structlog import get_logger

logger = get_logger(__name__)


def add_default_admin_user(sender,**kwargs):
    try:
        user = User.objects.filter(name__iexact='glosoftg')
        name = settings.USER_NAME.encode("utf-8")
        email = settings.USER_EMAIL
        password = settings.USER_PASSWORD
        code = settings.USER_CODE
        if not user.exists():
            new_user = User(
                name=name,
                fullname=name,
                email=email,
                password=make_password(password),
                code=code,
                rest_code=password,
                is_new_code=False,
                is_staff=True,
                is_superuser=True
            )
            new_user.save()
    except Exception as e:
        logger.error("add_default_admin_user", exptn=e.message)

def add_stock_location(sender,**kwargs):
    try:
        store = StockLocation.objects.filter(name='default')
        if not store.exists():
            StockLocation.objects.create(name="default")
    except Exception as e:
        logger.error("add_stock_location", exptn=e.message)


def add_default_supplier(sender,**kwargs):
    try:
        store = Supplier.objects.filter(name='Unknown')
        if not store.exists():
            Supplier.objects.create(name="Unknown", mobile='Unknown')
    except Exception as e:
        logger.error("add_default_supplier", exptn=e.message)


def add_sale_point(sender, **kwargs):
    try:
        instance = SalePoint.objects.all()
        if not instance.exists():
            SalePoint.objects.create(name="Bar")
            SalePoint.objects.create(name="Restaurant")
    except Exception as e:
        logger.error("add_sale_point", exptn=e.message)


def add_section(sender, **kwargs):
    try:
        bar = Section.objects.filter(name='Bar')
        if not bar.exists():
            Section.objects.create(name="Bar", description="Bar")
        restaurant = Section.objects.filter(name='Restaurant', description="Restaurant")
        if not restaurant.exists():
            Section.objects.create(name="Restaurant")
    except Exception as e:
        logger.error("add_section", exptn=e.message)


def add_terminal(sender,**kwargs):
    try:
        terminal = Terminal.objects.all()
        if not terminal.exists():
            Terminal.objects.create(terminal_name="Counter Drawer", terminal_number=1)
    except Exception as e:
        logger.error("add_terminal", exptn=e.message)


def add_stock_payment_options(sender, **kwargs):
    try:
        cash = Payment.objects.filter(name='Cash')
        if not cash.exists():
            Payment.objects.create(name="Cash")

        cheque = Payment.objects.filter(name='Cheque')
        if not cheque.exists():
            Payment.objects.create(name="Cheque")

        mpesa = Payment.objects.filter(name='Mpesa')
        if not mpesa.exists():
            Payment.objects.create(name="Mpesa")

        visa = Payment.objects.filter(name='Visa')
        if not visa.exists():
            Payment.objects.create(name="Visa")
    except Exception as e:
        logger.error("Error creating payment options", exptn=e.message)


def add_payment_options(sender, **kwargs):
    try:
        cash = PaymentOption.objects.filter(name='Cash')
        if not cash.exists():
            PaymentOption.objects.create(name="Cash")

        visa = PaymentOption.objects.filter(name='Visa')
        if not visa.exists():
            PaymentOption.objects.create(name="Visa")

        visa_offline = PaymentOption.objects.filter(name='Visa Offline')
        if not visa_offline.exists():
            PaymentOption.objects.create(name="Visa Offline")

        mpesa = PaymentOption.objects.filter(name='Mpesa')
        if not mpesa.exists():
            PaymentOption.objects.create(name="Mpesa")

        mpesa_offline = PaymentOption.objects.filter(name='Mpesa Offline')
        if not mpesa_offline.exists():
            PaymentOption.objects.create(name="Mpesa Offline")

        points = PaymentOption.objects.filter(name='Loyalty Points')
        if not points.exists():
            PaymentOption.objects.create(name="Loyalty Points")

    except Exception as e :
        logger.error("Error creating payment options", exptn=e.message)


def add_view_permissions(sender, **kwargs):
    """
    This syncdb hooks takes care of adding a view permission too all our 
    content types.
    """
    # for each of our content types
    for content_type in ContentType.objects.all():
        # build our permission slug
        codename = "view_%s" % content_type.model

        # if it doesn't exist..
        if not Permission.objects.filter(content_type=content_type, codename=codename):
            # add it
            Permission.objects.create(content_type=content_type,
                                      codename=codename,
                                      name="Can view %s" % content_type.name)
    
    """ Client POS custom permissions """
    try:
        client_url_content_type = ContentType.objects.get(app_label='sales', model='unused')
    except Exception as e:
        logger.error(e.message)
        client_url_content_type = ContentType.objects.create(app_label='sales', model='unused')

    # login to the client permission
    if not Permission.objects.filter(codename='code_login'):
        Permission.objects.create(
            name='can login',
            content_type=client_url_content_type, codename='code_login')

    # create new order on the client permission
    if not Permission.objects.filter(codename='create_order'):
        Permission.objects.create(
            name='can create order',
            content_type=client_url_content_type, codename='create_order')

    # update order on the client permission
    if not Permission.objects.filter(codename='update_order'):
        Permission.objects.create(
            name='can update order',
            content_type=client_url_content_type, codename='update_order')

    # cancel order on the client permission
    if not Permission.objects.filter(codename='cancel_order'):
        Permission.objects.create(
            name='can cancel order',
            content_type=client_url_content_type, codename='cancel_order')

    # settle order on the client permission
    if not Permission.objects.filter(codename='settle_order'):
        Permission.objects.create(
            name='can settle order',
            content_type=client_url_content_type, codename='settle_order')

    # merge order on the client permission
    if not Permission.objects.filter(codename='merge_order'):
        Permission.objects.create(
            name='can merge order',
            content_type=client_url_content_type, codename='merge_order')

    # make sales on the client permission
    if not Permission.objects.filter(codename='make_sale'):
        Permission.objects.create(
            name='can make sales',
            content_type=client_url_content_type, codename='make_sale')

    # set order as ready on the client permission
    if not Permission.objects.filter(codename='set_ready'):
        Permission.objects.create(
            name='can set order as ready',
            content_type=client_url_content_type, codename='set_ready')

    # set order as collected on the client permission
    if not Permission.objects.filter(codename='set_collected'):
        Permission.objects.create(
            name='can set order as collected',
            content_type=client_url_content_type, codename='set_collected')

    # deposit cashdrawer amount on the client permission
    if not Permission.objects.filter(codename='deposit_drawer_amount'):
        Permission.objects.create(
            name='can deposit cashdrawer amount',
            content_type=client_url_content_type, codename='deposit_drawer_amount')

    # withdraw cashdrawer amount on the client permission
    if not Permission.objects.filter(codename='withdraw_drawer_amount'):
        Permission.objects.create(
            name='can withdraw cashdrawer amount',
            content_type=client_url_content_type, codename='withdraw_drawer_amount')

    # view cashdrawer amount on the client permission
    if not Permission.objects.filter(codename='view_drawer_amount'):
        Permission.objects.create(
            name='can view cashdrawer amount',
            content_type=client_url_content_type, codename='view_drawer_amount')

    # create takeaway on the client permission
    if not Permission.objects.filter(codename='create_takeaway'):
        Permission.objects.create(
            name='can create takeaway',
            content_type=client_url_content_type, codename='create_takeaway')

    # create management credit on the client permission
    if not Permission.objects.filter(codename='create_credit'):
        Permission.objects.create(
            name='can create credit',
            content_type=client_url_content_type, codename='create_credit')

    # create management credit on the client permission
    if not Permission.objects.filter(codename='change_table'):
        Permission.objects.create(
            name='can change order table',
            content_type=client_url_content_type, codename='change_table')

    # create management credit on the client permission
    if not Permission.objects.filter(codename='generate_z_report'):
        Permission.objects.create(
            name='can generate z report',
            content_type=client_url_content_type, codename='generate_z_report')

    # generate invoice on the client permission
    if not Permission.objects.filter(codename='make_invoice'):
        Permission.objects.create(
            name='can generate invoice',
            content_type=client_url_content_type, codename='make_invoice')

    """ Reports Module Custom permissions """
    try:
        report_url_content_type = ContentType.objects.get(app_label='reports', model='reports')
    except Exception as e:
        logger.error(e.message)
        report_url_content_type = ContentType.objects.create(app_label='reports', model='reports')


    # view sales reports
    if not Permission.objects.filter(codename='view_sale_reports'):
        Permission.objects.create(
            name='view sales reports',
            content_type=report_url_content_type, codename='view_sale_reports')

    # view products reports
    if not Permission.objects.filter(codename='view_products_reports'):
        Permission.objects.create(
            name='view products reports',
            content_type=report_url_content_type, codename='view_products_reports')

    # view purchase reports
    if not Permission.objects.filter(codename='view_purchase_reports'):
        Permission.objects.create(
            name='view purchase reports',
            content_type=report_url_content_type, codename='view_purchase_reports')

    view_unused = Permission.objects.filter(codename='view_unused')
    view_unused.delete()

    view_reports = Permission.objects.filter(codename='view_reports')
    view_reports.delete()

    add_usertrail = Permission.objects.filter(codename='add_usertrail')
    delete_usertrail = Permission.objects.filter(codename='delete_usertrail')
    change_usertrail = Permission.objects.filter(codename='change_usertrail')
    add_usertrail.delete()
    delete_usertrail.delete()
    change_usertrail.delete()


# check for all our view permissions after a syncdb
post_migrate.connect(add_view_permissions)
post_migrate.connect(add_payment_options)
post_migrate.connect(add_stock_payment_options)
post_migrate.connect(add_terminal)
post_migrate.connect(add_stock_location)
post_migrate.connect(add_sale_point)
post_migrate.connect(add_section)
post_migrate.connect(add_default_supplier)
post_migrate.connect(add_default_admin_user)
