from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q

from ..views import staff_member_required
from ...table.models import Table
from ...decorators import user_trail
import json

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
def list(request):
    try:
        options = Table.objects.all().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(options, 10)
        try:
            options = paginator.page(page)
        except PageNotAnInteger:
            options = paginator.page(1)
        except InvalidPage:
            options = paginator.page(1)
        except EmptyPage:
            options = paginator.page(paginator.num_pages)
        data = {
            "options": options,
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed payment option', 'views')
        logger.info('User: ' + str(request.user.name) + 'accessed payment option page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/table/list.html', data)
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing payment options')


@staff_member_required
def add(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        if request.POST.get('name'):
            option = Table()
            option.name = request.POST.get('name')
            option.number = number
            option.save()
            data = {'name': option.name}
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps({'message': 'Invalid method'}))


@staff_member_required
def delete(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            if option.name == "Loyalty Points":
                pass
            else:
                option.delete()
                user_trail(request.user.name, 'deleted payment option : ' + str(option.name), 'delete')
                logger.info('deleted payment option: ' + str(option.name))
                return HttpResponse('success')
            return HttpResponse(json.dumps({'error': "Loyalty Points is not deletable"}),
                                content_type='application/json')
        except Exception, e:
            logger.error(e)
            return HttpResponse(e)


@staff_member_required
def edit(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            if request.POST.get('name'):
                if request.POST.get('name') != 'Loyalty Points':
                    option.name = request.POST.get('name')
                if request.POST.get('number'):
                    option.number = request.POST.get('number')
                option.save()
                user_trail(request.user.name, 'updated payment option : ' + str(option.name), 'delete')
                logger.info('updated payment option: ' + str(option.name))
                return HttpResponse('success')
            else:
                return HttpResponse('invalid response')
        except Exception, e:
            logger.error(e)
            return HttpResponse(e)


@staff_member_required
def detail(request, pk=None):
    if request.method == 'GET':
        try:
            option = get_object_or_404(Table, pk=pk)
            ctx = {'option': option}
            user_trail(request.user.name, 'access tabble details of: ' + str(option.name) + ' ', 'view')
            logger.info('access payment option details of: ' + str(option.name) + '  ')
            return TemplateResponse(request, 'dashboard/table/detail.html', ctx)
        except Exception, e:
            logger.error(e)
            return TemplateResponse(request, 'dashboard/table/detail.html', {'error': e})


def searchs(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            options = Table.objects.filter(
                Q(name__icontains=q) |
                Q(number__icontains=q)
            ).order_by('-id')
            paginator = Paginator(options, 10)
            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            if p2_sz:
                options = paginator.page(page)
                return TemplateResponse(request, 'dashboard/table/paginate.html', {'options': options, 'sz': sz})

            return TemplateResponse(request, 'dashboard/table/search.html',
                                    {'options': options, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = Table.objects.filter(name=type.name)
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request, 'dashboard/table/paginate.html', {'options': options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            return TemplateResponse(request, 'dashboard/table/p2.html',
                                    {'options': options, 'pn': paginator.num_pages, 'sz': list_sz,
                                     'gid': request.GET.get('gid')})

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        return TemplateResponse(request, 'dashboard/table/p2.html',
                                {'options': options, 'pn': paginator.num_pages, 'sz': 10,
                                 'gid': request.GET.get('gid')})
    else:
        try:
            options = Table.objects.all().order_by('-id')
            if list_sz:
                paginator = Paginator(options, int(list_sz))
                options = paginator.page(page)
                data = {
                    'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': 0
                }
                return TemplateResponse(request, 'dashboard/table/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/table/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/table/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()
