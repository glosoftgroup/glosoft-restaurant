from django.http import HttpResponse
from django.template.response import TemplateResponse
from saleor.dashboard.views import staff_member_required
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from .models import SalePoint
from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def points(request):
    try:
        points = SalePoint.objects.all().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(points, 10)
        try:
            points = paginator.page(page)
        except PageNotAnInteger:
            points = paginator.page(1)
        except InvalidPage:
            points = paginator.page(1)
        except EmptyPage:
            points = paginator.page(paginator.num_pages)
        data = {
            "points": points,
            "pn": paginator.num_pages
        }
        logger.info('User: ' + str(request.user.name) + 'accessed points page')
        return TemplateResponse(request, 'dashboard/salepoints/points.html', data)
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing points')


@staff_member_required
def add_point(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    sale_point = SalePoint(name=name, description=description)

    try:
        sale_point.save()
        logger.info('User: ' + str(request.user.name) + 'created point sale:' + str(name))
        return HttpResponse('success')
    except Exception as e:
        logger.info('Error when adding sale point')
        return HttpResponse(e)


@staff_member_required
def edit_point(request, pk):
    name = request.POST.get('name')
    description = request.POST.get('description')
    point = get_object_or_404(SalePoint, pk=pk)
    point.name = name
    point.description = description
    try:
        point.save()
        return HttpResponse('success')
    except Exception as e:
        return HttpResponse(e)


@staff_member_required
def delete_point(request, pk):
    point = get_object_or_404(SalePoint, pk=pk)
    if request.method == 'POST':
        try:
            point.delete()
            logger.info('deleted sale point: ' + str(point.name))
            return HttpResponse('success')
        except Exception, e:
            logger.error(e)
            return HttpResponse(e)
