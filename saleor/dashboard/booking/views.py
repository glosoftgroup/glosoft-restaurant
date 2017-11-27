from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q
from django.utils.translation import pgettext_lazy
from django.contrib import messages
from django.utils.http import is_safe_url

from ..views import staff_member_required
from saleor.booking.models import Book as Table
from saleor.room.models import Room
from .forms import RoomImageForm
from ...decorators import user_trail
import logging
import json

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

# global variables
table_name = 'Booking'


@staff_member_required
def list(request):
    global table_name
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
            "table_name": table_name,
            "options": options,            
            "pn": paginator.num_pages
        }
        user_trail(request.user.name, 'accessed '+table_name+' List', 'views')
        info_logger.info('User: ' + str(request.user.name) + 'accessed '+table_name+' List Page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/list.html', data)
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing payment options')


@staff_member_required
def add(request):
    global table_name
    if request.method == 'POST':
        if request.POST.get('pk'):
            instance = Table.objects.get(pk=request.POST.get('pk'))
        else:
            instance = Table()
        if request.POST.get('name'):
            instance.name = request.POST.get('name')
            if request.POST.get('price'):
                instance.price = request.POST.get('price')
            if request.POST.get('description'):
                instance.description = request.POST.get('description')
            instance.save()
            # add amenities
            if request.POST.get('amenities'):
                choices = json.loads(request.POST.get('amenities'))
                instance.amenities.clear()
                for choice in choices:
                    instance.amenities.add(choice)
                instance.save()

            data = {'name': instance.name}
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps({'message': 'Invalid method'}))
    else:
        ctx = {'table_name': table_name}
        return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/form.html', ctx)


@staff_member_required
def delete(request, pk=None):
    global table_name
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            option.delete()
            user_trail(request.user.name, 'deleted room : '+ str(option.name), 'delete')
            info_logger.info('deleted room: '+ str(option.name))
            return HttpResponse('success')
        except Exception, e:
            error_logger.error(e)
            return HttpResponse(e)


@staff_member_required
def edit(request, pk=None):
    global table_name
    room = get_object_or_404(Table, pk=pk)
    if request.method == 'GET':
        ctx = {'table_name': table_name, 'room': room}
        return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/form.html', ctx)
    if request.method == 'POST':
        try:
            if request.POST.get('name'):
                room.name = request.POST.get('name')
            if request.POST.get('price'):
                room.number = request.POST.get('price')
                room.save()
                user_trail(request.user.name, 'updated room : '+ str(room.name),'edit')
                info_logger.info('updated room : '+ str(room.name))
                return HttpResponse('success')
            else:
                return HttpResponse('invalid response')
        except Exception, e:
            error_logger.error(e)
            print e
            return HttpResponse(e)


@staff_member_required
def detail(request, pk=None):
    global table_name
    if request.method == 'GET':
        try:
            option = get_object_or_404(Table, pk=pk)
            ctx = {'option': option}
            user_trail(request.user.name, 'access Car details of: ' + str(option.name)+' ','view')
            info_logger.info('access car details of: ' + str(option.name)+'  ')
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/detail.html', ctx)
        except Exception, e:
            error_logger.error(e)
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/detail.html', {'error': e})


def searchs(request):
    global table_name
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
                Q(name__icontains=q)
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
                return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/paginate.html', {'options': options,'sz':sz})
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': sz,
                    'q': q}
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/search.html', data)


@staff_member_required
def paginate(request):
    global table_name
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        options = Table.objects.filter(name=type.name)
        if p2_sz:
            paginator = Paginator(options, int(p2_sz))
            options = paginator.page(page)
            return TemplateResponse(request,'dashboard/'+table_name.lower()+'/paginate.html',{'options':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': request.GET.get('gid')}
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/p2.html',data)

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        data = {'options': options,
                'pn': paginator.num_pages,
                'sz': 10,
                'gid': request.GET.get('gid')}
        return TemplateResponse(request,'dashboard/'+table_name.lower()+'/p2.html', data)
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
                return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/'+table_name.lower()+'/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()


@staff_member_required
def fetch_amenities(request):
    global table_name
    search = request.GET.get('search')
    dictionary = Room.objects.all().filter(name__icontains=str(search))
    l = []
    for instance in dictionary:
        # {"text": "Afghanistan", "value": "AF"},
        contact = {'text': instance.name, 'value': instance.id}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')

@staff_member_required
def compute_room_price(request):
    global table_name
    print type(request.POST.get('rooms'))
    print request.POST.get('rooms')
    rooms = json.loads(request.POST.get('rooms'))
    l = []
    total = 0
    for instance in rooms:
        room = Room.objects.get(pk=int(instance))
        total = total + room.price.gross
    return HttpResponse(json.dumps({"price": float(total)}), content_type='application/json')


