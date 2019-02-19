from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import datetime
from decimal import Decimal
from django.utils.dateformat import DateFormat
from operator import itemgetter
from ..views import staff_member_required
from ...sale.models import Sales, SoldItem, PaymentOption
from ...salepoints.models import SalePoint
from ...product.models import ProductVariant
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, default_logo

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_list(request):
    try:
        try:
            last_sale = Sales.objects.latest('id')
            last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
        except:
            last_date_of_sales = DateFormat(datetime.datetime.today()).format('Y-m-d')

        total_sales = SoldItem.objects.filter(sales__created__contains=last_date_of_sales).values('product_name',
                                                                                                  'product_category').annotate(
            c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(Sum('quantity')).order_by(
            '-quantity__sum')

        page = request.GET.get('page', 1)
        paginator = Paginator(total_sales, 10)
        try:
            total_sales = paginator.page(page)
        except PageNotAnInteger:
            total_sales = paginator.page(1)
        except InvalidPage:
            total_sales = paginator.page(1)
        except EmptyPage:
            total_sales = paginator.page(paginator.num_pages)

        points = SalePoint.objects.all()
        user_trail(request.user.name, 'accessed sales reports', 'view')
        logger.info('User: ' + str(request.user.name) + ' accessed the view product sales report page')
        return TemplateResponse(request, 'dashboard/reports/product_sales/product_sales.html',
                                {'points': points, 'pn': paginator.num_pages, 'sales': total_sales,
                                 'date': datetime.datetime.strptime(last_date_of_sales, '%Y-%m-%d').strftime(
                                     '%b %d, %Y')})
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
def sales_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    date = request.GET.get('gid')
    order = request.GET.get('order')
    point = request.GET.get('point')
    today_formart = DateFormat(datetime.date.today())
    today = today_formart.format('Y-m-d')
    margin = False

    if point and point != 'all':
        if point.lower() == "restaurant":
            all_items = SoldItem.objects.filter(counter__isnull=True)
        else:
            all_items = SoldItem.objects.filter(kitchen__isnull=True)
    else:
        all_items = SoldItem.objects.all()

    if date:
        try:
            itms = all_items.filter(sales__created__contains=date). \
                values('sku', 'unit_purchase', 'product_category', 'product_name').annotate(
                c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
                Sum('quantity'))
            if order == 'qlh':
                sales = itms.order_by('quantity__sum')
            elif order == 'mlh':
                items = itms
                total_items = []
                for t in items:
                    try:
                        itemPrice = t['unit_purchase'] * t['quantity__sum']
                    except Exception as e:
                        itemPrice = 0
                    totalSalesCost = t['total_cost__sum']
                    try:
                        unitMargin = totalSalesCost - (itemPrice)
                    except:
                        unitMargin = 0
                    t['unitMargin'] = unitMargin
                    total_items.append(t)
                sales = sorted(total_items, key=itemgetter('unitMargin'))
                margin = True
            elif order == 'mhl':
                items = itms
                total_items = []
                for t in items:
                    product = ProductVariant.objects.get(sku=t['sku'])
                    try:
                        itemPrice = t['unit_purchase'] * t['quantity__sum']
                    except Exception as e:
                        itemPrice = 0
                    totalSalesCost = t['total_cost__sum']
                    try:
                        unitMargin = totalSalesCost - (itemPrice)
                    except:
                        unitMargin = 0
                    t['unitMargin'] = unitMargin
                    total_items.append(t)
                sales = sorted(total_items, key=itemgetter('unitMargin'), reverse=True)
                margin = True
            else:
                sales = itms.order_by(
                    '-quantity__sum')

            if list_sz:
                paginator = Paginator(sales, int(list_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/p2.html',
                                        {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                         'pn': paginator.num_pages, 'sz': list_sz, 'gid': date,
                                         'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime(
                                             '%b %d, %Y')
                                         })

            if p2_sz and date:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/paginate.html',
                                        {'point': point, 'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime(
                                            '%b %d, %Y'),
                                         'margin': margin, 'order': order, 'sales': sales, 'gid': date})

            paginator = Paginator(sales, 10)
            sales = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/product_sales/p2.html',
                                    {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                     'pn': paginator.num_pages, 'sz': 10, 'gid': date,
                                     'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime(
                                         '%b %d, %Y'), 'today': today})

        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/product_sales/p2.html', {'point': point, 'date': date})

    else:
        try:
            last_sale = Sales.objects.latest('id')
            last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
            itms = all_items.filter(sales__created__contains=last_date_of_sales). \
                values('sku', 'product_category', 'product_name').annotate(
                c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
                Sum('quantity'))
            if order == 'qlh':
                sales = itms.order_by('quantity__sum')
            elif order == 'mlh':
                items = itms
                total_items = []
                for t in items:
                    product = ProductVariant.objects.get(sku=t['sku'])
                    try:
                        itemPrice = product.get_cost_price().gross * t['quantity__sum']
                    except ValueError as e:
                        itemPrice = product.get_cost_price() * t['quantity__sum']
                    except:
                        itemPrice = 0
                    totalSalesCost = t['total_cost__sum']
                    try:
                        unitMargin = totalSalesCost - (itemPrice)
                    except:
                        unitMargin = 0
                    t['unitMargin'] = unitMargin
                    total_items.append(t)
                sales = sorted(total_items, key=itemgetter('unitMargin'))
                margin = True
            elif order == 'mhl':
                items = itms
                total_items = []
                for t in items:
                    product = ProductVariant.objects.get(sku=t['sku'])
                    try:
                        itemPrice = product.get_cost_price().gross * t['quantity__sum']
                    except ValueError as e:
                        itemPrice = product.get_cost_price() * t['quantity__sum']
                    except:
                        itemPrice = 0
                    totalSalesCost = t['total_cost__sum']
                    try:
                        unitMargin = totalSalesCost - (itemPrice)
                    except:
                        unitMargin = 0
                    t['unitMargin'] = unitMargin
                    total_items.append(t)
                sales = sorted(total_items, key=itemgetter('unitMargin'), reverse=True)
                margin = True
            else:
                sales = itms.order_by(
                    '-quantity__sum')

            if list_sz:
                paginator = Paginator(sales, int(list_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/p2.html',
                                        {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                         'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                         'date': datetime.datetime.strptime(last_date_of_sales, '%Y-%m-%d').strftime(
                                             '%b %d, %Y')
                                         })
            else:
                paginator = Paginator(sales, 10)
            if p2_sz:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/paginate.html',
                                        {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                         'date': datetime.datetime.strptime(last_date_of_sales, '%Y-%m-%d').strftime(
                                             '%b %d, %Y')})

            try:
                sales = paginator.page(page)
            except PageNotAnInteger:
                sales = paginator.page(1)
            except InvalidPage:
                sales = paginator.page(1)
            except EmptyPage:
                sales = paginator.page(1)
            return TemplateResponse(request, 'dashboard/reports/product_sales/paginate.html',
                                    {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                     'date': datetime.datetime.strptime(
                                         last_date_of_sales,
                                         '%Y-%m-%d').strftime(
                                         '%b %d, %Y')})
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/product_sales/p2.html', {'point': point})


@staff_member_required
def sales_search(request):
    if request.is_ajax():
        page = int(request.GET.get('page', 1))
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        order = request.GET.get('order')
        point = request.GET.get('point')
        margin = False
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if request.GET.get('gid'):
            date = request.GET.get('gid')
        else:
            try:
                last_sale = Sales.objects.latest('id')
                date = DateFormat(last_sale.created).format('Y-m-d')
            except:
                date = DateFormat(datetime.datetime.today()).format('Y-m-d')

        if point and point != 'all':
            try:
                all_items = SoldItem.objects.filter(sale_point__name__icontains=point)
            except:
                all_items = SoldItem.objects.all()
        else:
            all_items = SoldItem.objects.all()

        if q is not None:
            all_sales = all_items.filter(
                Q(product_name__icontains=q) |
                Q(product_category__icontains=q)).filter(sales__created__contains=date). \
                values('sku', 'product_category', 'product_name'). \
                annotate(c=Count('product_name', distinct=True)).annotate(Sum('total_cost')). \
                annotate(Sum('quantity'))

            if order == 'qlh':
                sales = all_sales.order_by('quantity__sum')
            elif order == 'mlh':
                items = all_sales
                total_items = []
                for t in items:
                    product = ProductVariant.objects.get(sku=t['sku'])
                    try:
                        itemPrice = product.get_cost_price().gross * t['quantity__sum']
                    except ValueError as e:
                        itemPrice = product.get_cost_price() * t['quantity__sum']
                    except:
                        itemPrice = 0
                    totalSalesCost = t['total_cost__sum']
                    try:
                        unitMargin = totalSalesCost - (itemPrice)
                    except:
                        unitMargin = 0
                    t['unitMargin'] = unitMargin
                    total_items.append(t)
                sales = sorted(total_items, key=itemgetter('unitMargin'))
                margin = True
            elif order == 'mhl':
                items = all_sales
                total_items = []
                for t in items:
                    product = ProductVariant.objects.get(sku=t['sku'])
                    try:
                        itemPrice = product.get_cost_price().gross * t['quantity__sum']
                    except ValueError as e:
                        itemPrice = product.get_cost_price() * t['quantity__sum']
                    except:
                        itemPrice = 0
                    totalSalesCost = t['total_cost__sum']
                    try:
                        unitMargin = totalSalesCost - (itemPrice)
                    except:
                        unitMargin = 0
                    t['unitMargin'] = unitMargin
                    total_items.append(t)
                sales = sorted(total_items, key=itemgetter('unitMargin'), reverse=True)
                margin = True
            else:
                sales = all_sales.order_by('-quantity__sum')

            if p2_sz:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/paginate.html',
                                        {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                         'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b %d, %Y')})

            if list_sz:
                paginator = Paginator(sales, int(list_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/search.html',
                                        {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                         'pn': paginator.num_pages, 'sz': list_sz,
                                         'gid': request.GET.get('gid'), 'q': q,
                                         'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime(
                                             '%b %d, %Y')})

            paginator = Paginator(sales, 10)
            sales = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/product_sales/search.html',
                                    {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                     'pn': paginator.num_pages, 'sz': sz,
                                     'gid': request.GET.get('gid'),
                                     'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime(
                                         '%b %d, %Y')})

            paginator = Paginator(sales, 10)
            try:
                sales = paginator.page(page)
            except PageNotAnInteger:
                sales = paginator.page(1)
            except InvalidPage:
                sales = paginator.page(1)
            except EmptyPage:
                sales = paginator.page(paginator.num_pages)
            if p2_sz:
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/product_sales/paginate.html',
                                        {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                         'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b %d, %Y')})

            return TemplateResponse(request, 'dashboard/reports/product_sales/search.html',
                                    {'point': point, 'margin': margin, 'order': order, 'sales': sales,
                                     'pn': paginator.num_pages, 'sz': sz,
                                     'q': q,
                                     'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b %d, %Y')})


@staff_member_required
def sales_list_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')
        order = request.GET.get('order')
        point = request.GET.get('point')
        margin = False

        if gid:
            date = request.GET.get('gid')
            gid = gid
        else:
            gid = None
            try:
                last_sale = Sales.objects.latest('id')
                date = DateFormat(last_sale.created).format('Y-m-d')
            except:
                date = DateFormat(datetime.datetime.today()).format('Y-m-d')

        date_sales = Sales.objects.filter(created__icontains=date)

        if point and point != 'all':
            try:
                all_items = SoldItem.objects.filter(sale_point__name__icontains=point)
            except:
                all_items = SoldItem.objects.all()
        else:
            all_items = SoldItem.objects.all()

        if q is not None:
            all_sales = all_items.filter(
                Q(product_name__icontains=q) |
                Q(product_category__icontains=q)).filter(sales__created__contains=date). \
                values('sku', 'product_category', 'product_name'). \
                annotate(c=Count('product_name', distinct=True)).annotate(Sum('total_cost')). \
                annotate(Sum('quantity'))
        else:
            all_sales = all_items.filter(sales__created__contains=date). \
                values('sku', 'product_category', 'product_name'). \
                annotate(c=Count('product_name', distinct=True)).annotate(Sum('total_cost')). \
                annotate(Sum('quantity'))

        if order == 'qlh':
            sales = all_sales.order_by('quantity__sum')
        elif order == 'mlh':
            items = all_sales
            total_items = []
            for t in items:
                product = ProductVariant.objects.get(sku=t['sku'])
                try:
                    itemPrice = product.get_cost_price().gross * t['quantity__sum']
                except ValueError as e:
                    itemPrice = product.get_cost_price() * t['quantity__sum']
                except:
                    itemPrice = 0
                totalSalesCost = t['total_cost__sum']
                try:
                    unitMargin = totalSalesCost - (itemPrice)
                except:
                    unitMargin = 0
                t['unitMargin'] = unitMargin
                total_items.append(t)
            sales = sorted(total_items, key=itemgetter('unitMargin'))
            margin = True
        elif order == 'mhl':
            items = all_sales
            total_items = []
            for t in items:
                product = ProductVariant.objects.get(sku=t['sku'])
                try:
                    itemPrice = product.get_cost_price().gross * t['quantity__sum']
                except ValueError as e:
                    itemPrice = product.get_cost_price() * t['quantity__sum']
                except:
                    itemPrice = 0
                totalSalesCost = t['total_cost__sum']
                try:
                    unitMargin = totalSalesCost - (itemPrice)
                except:
                    unitMargin = 0
                t['unitMargin'] = unitMargin
                total_items.append(t)
            sales = sorted(total_items, key=itemgetter('unitMargin'), reverse=True)
            margin = True
        else:
            sales = all_sales.order_by('-quantity__sum')

        if point == 'all':
            point = 'all item sales'

        payments = []

        for i in date_sales:
            for j in i.payment_data:
                try:
                    payment_name = PaymentOption.objects.get(pk=int(j['payment_id'])).name
                except:
                    payment_name = int(j['payment_id'])

                if any(d['payment_id'] == int(j['payment_id']) for d in payments):
                    for d in payments:
                        if d['payment_id'] == int(j['payment_id']):
                            d['value'] += Decimal(j['value'])
                else:
                    payments.append(
                        {"payment_id": int(j["payment_id"]), "value": Decimal(j["value"]), "name": payment_name})

        total_sales = all_sales.aggregate(Sum("total_cost__sum"))["total_cost__sum__sum"]
        total_tax = all_sales.aggregate(Sum("tax"))["tax__sum"]

        point = point.upper()

        img = default_logo()
        data = {
            'today': datetime.date.today(),
            'sales': sales,
            'puller': request.user,
            'image': img,
            'gid': gid,
            'date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%b %d, %Y'),
            'margin': margin,
            'point': point,
            "payments": payments,
            "total_sales": total_sales,
            "total_tax": total_tax
        }
        pdf = render_to_pdf('dashboard/reports/product_sales/pdf/list.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
