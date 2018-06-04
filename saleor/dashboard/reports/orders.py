import logging
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.utils.dateformat import DateFormat
from ..views import staff_member_required
from ...salepoints.models import SalePoint
from ...section.models import Section
from ...orders.models import Orders, OrderedItem
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, default_logo

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def orders_list(request):
	try:
		try:
			last_order = Orders.objects.latest('id')
			last_date_of_orders = DateFormat(last_order.created).format('Y-m-d')
		except:
			last_date_of_orders = DateFormat(datetime.datetime.today()).format('Y-m-d')

		all_orders = Orders.objects.filter(created__contains=last_date_of_orders)
		total_orders = []
		for order in all_orders:
			quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Sum('quantity'))
			setattr(order, 'quantity', quantity['c'])
			total_orders.append(order)

		page = request.GET.get('page', 1)
		paginator = Paginator(total_orders, 10)
		try:
			total_orders = paginator.page(page)
		except PageNotAnInteger:
			total_orders = paginator.page(1)
		except InvalidPage:
			total_orders = paginator.page(1)
		except EmptyPage:
			total_orders = paginator.page(paginator.num_pages)
		points = SalePoint.objects.all()
		user_trail(request.user.name, 'accessed sales reports', 'view')
		info_logger.info('User: ' + str(request.user.name) + ' accessed the view sales report page')
		return TemplateResponse(request, 'dashboard/reports/orders/sales_list.html',
								{'pn': paginator.num_pages, 'orders': total_orders,
								 "date": last_date_of_orders, 'points':points})
	except ObjectDoesNotExist as e:
		error_logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def orders_detail(request, pk=None, point=None):
	if point == '0':
		sale_point = None
	else:
		sale_point = SalePoint.objects.get(pk=int(point))

	try:
		order = Orders.objects.get(pk=pk)

		sale_points = []
		order_items = []
		for n in Section.objects.all():
			sale_points.append(n.name)

		all_sale_points = list(set(sale_points))

		# for i in all_sale_points:
		# 	items = OrderedItem.objects.filter(orders=order, sale_point__name=i)
		# 	if items.exists():
		# 		try:
		# 			totals = items.aggregate(Sum('total_cost'))['total_cost__sum']
		# 		except:
		# 			totals = 0
		# 		pks = SalePoint.objects.get(name=i).pk
		# 		order_items.append({'name': i, 'pk':pks, 'items':items, 'amount': totals})

		counter_items = OrderedItem.objects.filter(orders=order, kitchen__isnull=True)
		if counter_items.exists():
			try:
				totals = counter_items.aggregate(Sum('total_cost'))['total_cost__sum']
			except:
				totals = 0
			bar = Section.objects.get(name="Bar")
			order_items.append({'name': bar.name, 'pk': bar.pk, 'items': counter_items, 'amount': totals})

		kitchen_items = OrderedItem.objects.filter(orders=order, counter__isnull=True)
		if kitchen_items.exists():
			try:
				totals = kitchen_items.aggregate(Sum('total_cost'))['total_cost__sum']
			except:
				totals = 0
			rest = Section.objects.get(name="Restaurant")
			order_items.append({'name': rest.name, 'pk': rest.pk, 'items': kitchen_items, 'amount': totals})

		data = {
			'order': order,
			'epp':order_items,
			'point':sale_point,
			'point_pk':point
		}
		return TemplateResponse(request, 'dashboard/reports/orders/details.html', data)
	except ObjectDoesNotExist as e:
		error_logger.error(e)


@staff_member_required
@permission_decorator('reports.view_sales_reports')
def order_detail_pdf(request, pk=None, point=None):
	if point == '0':
		sale_point = None
		print 'true'
	else:
		print 'false'
		sale_point = SalePoint.objects.get(pk=int(point))
	try:
		order = Orders.objects.get(pk=pk)
		sale_points = []
		order_items = []
		for n in Section.objects.all():
			sale_points.append(n.name)

		all_sale_points = list(set(sale_points))
		""" TODO: remember to delete after kitchen verification"""
		# for i in all_sale_points:
		# 	items = OrderedItem.objects.filter(orders=order, sale_point__name=i)
		# 	try:
		# 		totals = items.aggregate(Sum('total_cost'))['total_cost__sum']
		# 	except:
		# 		totals = 0
		# 	order_items.append({'name': i, 'items':items, 'amount': totals})
		counter_items = OrderedItem.objects.filter(orders=order, kitchen__isnull=True)
		if counter_items.exists():
			try:
				totals = counter_items.aggregate(Sum('total_cost'))['total_cost__sum']
			except:
				totals = 0
			bar = Section.objects.get(name="Bar")
			order_items.append({'name': bar.name, 'pk': bar.pk, 'items': counter_items, 'amount': totals})

		kitchen_items = OrderedItem.objects.filter(orders=order, counter__isnull=True)
		if kitchen_items.exists():
			try:
				totals = kitchen_items.aggregate(Sum('total_cost'))['total_cost__sum']
			except:
				totals = 0
			rest = Section.objects.get(name="Restaurant")
			order_items.append({'name': rest.name, 'pk': rest.pk, 'items': kitchen_items, 'amount': totals})

		img = default_logo()
		data = {
			'today': datetime.date.today(),
			'epp': order_items,
			'order': order,
			'puller': request.user,
			'image': img,
			'point':sale_point
		}
		pdf = render_to_pdf('dashboard/reports/orders/pdf/pdf.html',data)
		return HttpResponse(pdf, content_type='application/pdf')
	except ObjectDoesNotExist as e:
		error_logger.error(e)



@staff_member_required
def orders_paginate(request):
	page = int(request.GET.get('page'))
	list_sz = request.GET.get('size')
	p2_sz = request.GET.get('psize')
	date = request.GET.get('gid')
	point = request.GET.get('point')
	today_formart = DateFormat(datetime.date.today())
	today = today_formart.format('Y-m-d')
	ts = Orders.objects.filter(created__icontains=today)
	tsum = ts.aggregate(Sum('total_net'))

	if date:
		try:
			all_ordersd = Orders.objects.filter(created__icontains=date).order_by('-id')
			that_date_sum = Orders.objects.filter(created__contains=date).aggregate(Sum('total_net'))
			orders = []
			if point and point != 'all':
				for i in Orders.objects.filter(created__contains=date):
					p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
						c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
						Sum('quantity'))
					setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
					setattr(i, 'point', str(point))
					setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

					if p.exists():
						orders.append(i)
				point = SalePoint.objects.get(name=point)
				point_pk=point.pk
			else:
				for order in all_ordersd:
					quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
					setattr(order, 'quantity', quantity['c'])
					orders.append(order)
				point_pk = 0
				point = point

			if list_sz:
				paginator = Paginator(orders, int(list_sz))
				orders = paginator.page(page)
				return TemplateResponse(request, 'dashboard/reports/orders/p2.html',
										{'point': point, 'point_pk': point_pk, 'orders': orders,
										 'pn': paginator.num_pages, 'sz': list_sz, 'gid': date,
										 'tsum': tsum})

			if p2_sz and date:
				paginator = Paginator(orders, int(p2_sz))
				orders = paginator.page(page)
				return TemplateResponse(request, 'dashboard/reports/orders/paginate.html', {'point_pk':point_pk,'orders': orders, 'gid': date})

			paginator = Paginator(orders, 10)
			orders = paginator.page(page)
			return TemplateResponse(request, 'dashboard/reports/orders/p2.html',
									{'point':point, 'point_pk':point_pk, 'orders': orders, 'pn': paginator.num_pages, 'sz': 10, 'gid': date,
									 'tsum': tsum, 'that_date_sum': that_date_sum, 'date': date, 'today': today})

		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/orders/p2.html', {'point':point, 'point_pk':point_pk, 'date': date})

	else:
		try:
			last_order = Orders.objects.latest('id')
			last_date_of_order = DateFormat(last_order.created).format('Y-m-d')
			all_sales = Orders.objects.filter(created__contains=last_date_of_order)
			orders = []
			if point and point != 'all':
				for i in Orders.objects.filter(created__contains=last_date_of_order):
					p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
						c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
						Sum('quantity'))
					setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
					setattr(i, 'point', str(point))
					setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

					if p.exists():
						orders.append(i)
				point = SalePoint.objects.get(name=point)
				point_pk = point.pk
			else:
				for order in all_sales:
					quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
					setattr(order, 'quantity', quantity['c'])
					orders.append(order)
				point_pk = 0
				point = point



			if list_sz:
				paginator = Paginator(orders, int(list_sz))
				orders = paginator.page(page)
				return TemplateResponse(request, 'dashboard/reports/orders/p2.html',
										{'point':point, 'point_pk':point_pk, 'orders': orders, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
										 'tsum': tsum})
			else:
				paginator = Paginator(orders, 10)

			if p2_sz:
				paginator = Paginator(orders, int(p2_sz))
				orders = paginator.page(page)
				return TemplateResponse(request, 'dashboard/reports/orders/paginate.html', {'point_pk':point_pk,'orders': orders})

			try:
				orders = paginator.page(page)
			except PageNotAnInteger:
				orders = paginator.page(1)
			except InvalidPage:
				orders = paginator.page(1)
			except EmptyPage:
				orders = paginator.page(1)
			return TemplateResponse(request, 'dashboard/reports/orders/paginate.html', {'point_pk':point_pk,'orders': orders})
		except ObjectDoesNotExist as e:
			return TemplateResponse(request, 'dashboard/reports/orders/p2.html', {'point':point, 'date': date})


@staff_member_required
def orders_search(request):
	if request.is_ajax():
		page = int(request.GET.get('page', 1))
		list_sz = request.GET.get('size')
		p2_sz = request.GET.get('psize')
		point = request.GET.get('point')
		q = request.GET.get('q')
		if list_sz is None:
			sz = 10
		else:
			sz = list_sz

		if q is not None:
			all_orders = Orders.objects.filter(
				Q(invoice_number__icontains=q) |
				Q(sale_point__name__icontains=q) |
				Q(status__icontains=q) |
				Q(table__name__icontains=q) |
				Q(carry__icontains=q) |
				Q(ordered_items__product_name__icontains=q) |
				Q(user__email__icontains=q) |
				Q(user__name__icontains=q)).order_by('id').distinct()
			orders = []

			if request.GET.get('gid'):
				corders = all_orders.filter(created__icontains=request.GET.get('gid'))
				if point and point != 'all':
					for i in corders:
						p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
							c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
							Sum('quantity'))
						setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
						setattr(i, 'point', str(point))
						setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

						if p.exists():
							orders.append(i)
					point = SalePoint.objects.get(name=point)
					point_pk = point.pk
				else:
					for order in corders:
						quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
						setattr(order, 'quantity', quantity['c'])
						orders.append(order)
					point_pk = 0
					point = point

				if p2_sz:
					paginator = Paginator(orders, int(p2_sz))
					orders = paginator.page(page)
					return TemplateResponse(request, 'dashboard/reports/orders/paginate.html', {'point_pk':point_pk, 'orders': orders})

				if list_sz:
					paginator = Paginator(orders, int(list_sz))
					orders = paginator.page(page)
					return TemplateResponse(request, 'dashboard/reports/orders/search.html',
											{'point_pk':point_pk, 'point':point, 'orders': orders, 'pn': paginator.num_pages, 'sz': list_sz,
											 'gid': request.GET.get('gid'), 'q': q})

				paginator = Paginator(orders, 10)
				orders = paginator.page(page)
				return TemplateResponse(request, 'dashboard/reports/orders/search.html',
										{'point_pk':point_pk, 'point':point, 'orders': orders, 'pn': paginator.num_pages, 'sz': sz,
										 'gid': request.GET.get('gid')})

			else:
				if point and point != 'all':
					for i in all_orders:
						p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
							c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
							Sum('quantity'))
						setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
						setattr(i, 'point', str(point))
						setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

						if p.exists():
							orders.append(i)
					point = SalePoint.objects.get(name=point)
					point_pk = point.pk
				else:
					for order in all_orders:
						quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
						setattr(order, 'quantity', quantity['c'])
						orders.append(order)
					point_pk = 0
					point = point

				if list_sz:
					print ('lst')
					paginator = Paginator(orders, int(list_sz))
					orders = paginator.page(page)
					return TemplateResponse(request, 'dashboard/reports/orders/search.html',
											{'point_pk':point_pk,'point':point, 'orders': orders, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
											 'q': q})

				if p2_sz:
					print ('pst')
					paginator = Paginator(orders, int(p2_sz))
					orders = paginator.page(page)
					return TemplateResponse(request, 'dashboard/reports/orders/paginate.html', {'point_pk':point_pk,'orders': orders})

				paginator = Paginator(orders, 10)
				try:
					orders = paginator.page(page)
				except PageNotAnInteger:
					orders = paginator.page(1)
				except InvalidPage:
					orders = paginator.page(1)
				except EmptyPage:
					orders = paginator.page(paginator.num_pages)
				if p2_sz:
					orders = paginator.page(page)
					return TemplateResponse(request, 'dashboard/reports/orders/paginate.html', {'point_pk':point_pk,'orders': orders})

				return TemplateResponse(request, 'dashboard/reports/orders/search.html',
										{'point_pk':point_pk,'point':point, 'orders': orders, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def orders_list_pdf(request):

	if request.is_ajax():
		q = request.GET.get( 'q' )
		gid = request.GET.get('gid')
		point = request.GET.get('point')

		if gid:
			gid = gid
		else:
			gid = None

		orders = []
		if q is not None:
			all_orders = Orders.objects.filter(
				Q(invoice_number__icontains=q) |
				Q(terminal__terminal_name__icontains=q) |
				Q(created__icontains=q) |
				Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
				Q(ordered_items__product_name__icontains=q) |
				Q(user__email__icontains=q) |
				Q(user__name__icontains=q)).order_by('id').distinct()

			if gid:
				corders = all_orders.filter(created__icontains=gid)
				if point and point != 'all':
					for i in corders:
						p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
							c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
							Sum('quantity'))
						setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
						setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

						if p.exists():
							orders.append(i)
					point = SalePoint.objects.get(name=point)
				else:
					for order in corders:
						quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
						setattr(order, 'quantity', quantity['c'])
						orders.append(order)
					point = point
			else:
				if point and point != 'all':
					for i in all_orders:
						p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
							c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
							Sum('quantity'))
						setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
						setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

						if p.exists():
							orders.append(i)
					point = SalePoint.objects.get(name=point)
				else:
					for order in all_orders:
						quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
						setattr(order, 'quantity', quantity['c'])
						orders.append(order)
					point = point


		elif gid:
			corders = Orders.objects.filter(created__icontains=gid)
			if point and point != 'all':
				for i in corders:
					p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
						c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
						Sum('quantity'))
					setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
					setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

					if p.exists():
						orders.append(i)
				point = SalePoint.objects.get(name=point)
			else:
				for order in corders:
					quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
					setattr(order, 'quantity', quantity['c'])
					orders.append(order)
				point = point
		else:
			try:
				last_order = Orders.objects.latest('id')
				gid = DateFormat(last_order.created).format('Y-m-d')
			except:
				gid = DateFormat(datetime.datetime.today()).format('Y-m-d')

			corders = Orders.objects.filter(created__icontains=gid)
			if point and point != 'all':
				for i in corders:
					p = OrderedItem.objects.filter(orders__pk=i.pk, sale_point__name=point).annotate(
						c=Count('product_name', distinct=True)).annotate(Sum('total_cost')).annotate(
						Sum('quantity'))
					setattr(i, 'quantity', p.aggregate(c=Count('sku'))['c'])
					setattr(i, 'total_net', p.aggregate(Sum('total_cost'))['total_cost__sum'])

					if p.exists():
						orders.append(i)
				point = SalePoint.objects.get(name=point)
			else:
				for order in corders:
					quantity = OrderedItem.objects.filter(orders=order).aggregate(c=Count('sku'))
					setattr(order, 'quantity', quantity['c'])
					orders.append(order)
				point = point

		img = default_logo
		data = {
			'today': datetime.date.today(),
			'orders': orders,
			'puller': request.user,
			'image': img,
			'gid':gid,
			'point':point
		}
		pdf = render_to_pdf('dashboard/reports/orders/pdf/saleslist_pdf.html', data)
		return HttpResponse(pdf, content_type='application/pdf')