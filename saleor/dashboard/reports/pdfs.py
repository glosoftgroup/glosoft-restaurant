import random
import csv
import datetime
import re
from django.http import HttpResponse
from django.template.defaultfilters import date
from django.db.models import Count, Sum, Q
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.utils.dateformat import DateFormat
from django.utils.encoding import smart_str
from ...salepoints.models import SalePoint
from ...section.models import Section
from ..views import staff_member_required
from ...userprofile.models import User
from ...sale.models import Sales, SoldItem
from ...decorators import permission_decorator
from ...utils import render_to_pdf, default_logo

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def chart_pdf(request, image):
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    ImageData = image
    ImageData = dataUrlPattern.match(ImageData).group(2)

    users = User.objects.all()
    data = {
        'today': date.today(),
        'users': users,
        'puller': request.user,
        'image': ImageData
    }
    pdf = render_to_pdf('dashboard/reports/sales/charts/pdf/pdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
def sales_export_csv(request, image):
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    ImageData = image
    ImageData = dataUrlPattern.match(ImageData).group(2)
    fh = open("imageToSave.png", "wb")
    fh.write(ImageData.decode('base64'))
    fh.close()

    pdfname = 'users' + str(random.random())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + pdfname + '.csv"'
    qs = User.objects.all()
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Name"),
        smart_str(u"Email"),
        smart_str(u"Image"),
    ])
    for obj in qs:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.name),
            smart_str(obj.email),
            smart_str(fh),
        ])
    return response


@staff_member_required
def sales_list_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')
        point = request.GET.get('point')

        if gid:
            gid = gid
        else:
            gid = None

        sales = []
        if q is not None:
            all_sales = Sales.objects.filter(
                Q(invoice_number__icontains=q) |
                Q(terminal__terminal_name__icontains=q) |
                Q(created__icontains=q) |
                Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
                Q(solditems__product_name__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__name__icontains=q)).order_by('id').distinct()

            if gid:
                csales = all_sales.filter(created__icontains=gid)
                if point and point != 'all':
                    for i in csales:
                        p = SoldItem.objects.filter(sales__pk=i.pk, sale_point__name=point).annotate(
                            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
                            Sum('quantity'))
                        setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
                        setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])
                        setattr(i, 'total_tax', p.aggregate(Sum('tax'))['tax__sum'])

                        if p.exists():
                            sales.append(i)
                    point = SalePoint.objects.get(name=point)
                else:
                    for sale in csales:
                        quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                        setattr(sale, 'quantity', quantity['c'])
                        sales.append(sale)
                    point = point
            else:
                if point and point != 'all':
                    for i in all_sales:
                        p = SoldItem.objects.filter(sales__pk=i.pk, sale_point__name=point).annotate(
                            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
                            Sum('quantity'))
                        setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
                        setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])
                        setattr(i, 'total_tax', p.aggregate(Sum('tax'))['tax__sum'])

                        if p.exists():
                            sales.append(i)
                    point = SalePoint.objects.get(name=point)
                else:
                    for sale in all_sales:
                        quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                        setattr(sale, 'quantity', quantity['c'])
                        sales.append(sale)
                    point = point

        elif gid:
            csales = Sales.objects.filter(created__icontains=gid)
            if point and point != 'all':
                for i in csales:
                    p = SoldItem.objects.filter(sales__pk=i.pk, sale_point__name=point).annotate(
                        c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
                        Sum('quantity'))
                    setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
                    setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])
                    setattr(i, 'total_tax', p.aggregate(Sum('tax'))['tax__sum'])

                    if p.exists():
                        sales.append(i)
                point = SalePoint.objects.get(name=point)
            else:
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)
                point = point
        else:
            try:
                last_sale = Sales.objects.latest('id')
                gid = DateFormat(last_sale.created).format('Y-m-d')
            except:
                gid = DateFormat(datetime.datetime.today()).format('Y-m-d')

            csales = Sales.objects.filter(created__icontains=gid)
            if point and point != 'all':
                for i in csales:
                    p = SoldItem.objects.filter(sales__pk=i.pk, sale_point__name=point).annotate(
                        c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
                        Sum('quantity'))
                    setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
                    setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])
                    setattr(i, 'total_tax', p.aggregate(Sum('tax'))['tax__sum'])

                    if p.exists():
                        sales.append(i)
                point = SalePoint.objects.get(name=point)
            else:
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    sales.append(sale)
                point = point

        img = default_logo
        data = {
            'today': date.today(),
            'sales': sales,
            'puller': request.user,
            'image': img,
            'gid': gid,
            'point': point
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/saleslist_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_detail(request, pk=None, point=None):
    if point == '0':
        sale_point = None
        print 'true'
    else:
        print 'false'
        sale_point = SalePoint.objects.get(pk=int(point))

    try:
        sale = Sales.objects.get(pk=pk)
        img = default_logo()

        sale_points = []
        sale_items = []
        for n in Section.objects.all():
            sale_points.append(n.name)

        all_sale_points = list(set(sale_points))

        # for i in all_sale_points:
        # 	items = SoldItem.objects.filter(sales=sale, sale_point__name=i)
        # 	try:
        # 		totals = items.aggregate(Sum('total_cost'))['total_cost__sum']
        # 	except:
        # 		totals = 0
        # 	sale_items.append({'name': i, 'items': items, 'amount': totals})
        counter_items = SoldItem.objects.filter(sales=sale, kitchen__isnull=True)
        if counter_items.exists():
            try:
                totals = counter_items.aggregate(Sum('total_cost'))['total_cost__sum']
            except:
                totals = 0
            bar = Section.objects.get(name="Bar")
            sale_items.append({'name': bar.name, 'pk': bar.pk, 'items': counter_items, 'amount': totals})

        kitchen_items = SoldItem.objects.filter(sales=sale, counter__isnull=True)
        if kitchen_items.exists():
            try:
                totals = kitchen_items.aggregate(Sum('total_cost'))['total_cost__sum']
            except:
                totals = 0
            rest = Section.objects.get(name="Restaurant")
            sale_items.append({'name': rest.name, 'pk': rest.pk, 'items': kitchen_items, 'amount': totals})

        data = {
            'today': date.today(),
            'epp': sale_items,
            'sale': sale,
            'puller': request.user,
            'image': img,
            'point': sale_point,
            'point_pk': point
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_category(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = default_logo()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/category.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_items(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = default_logo()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/items.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


# discount
@staff_member_required
@permission_decorator('reports.view_sales_reports')
def discount_items(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = default_logo()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/discount.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_user(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = default_logo()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/user.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def sales_tills(request):
    try:
        image = request.GET.get('image')
        sales_date = request.GET.get('date')
        if not sales_date:
            sales_date = None

        img = default_logo()
        data = {
            'today': date.today(),
            'puller': request.user,
            'image': img,
            'category': image,
            'sales_date': sales_date
        }
        pdf = render_to_pdf('dashboard/reports/sales/pdf/till.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)
