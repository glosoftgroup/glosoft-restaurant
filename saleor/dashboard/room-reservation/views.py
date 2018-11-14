from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import pgettext_lazy
from django.contrib import messages
from django.utils.http import is_safe_url

from ..views import staff_member_required
from saleor.room.models import Room as Table
from saleor.booking.models import Book, BookingHistory
from saleor.room.models import RoomAmenity, RoomImage, Package, Pricing
from saleor.site.models import SiteSettings
from .forms import RoomImageForm
from ...decorators import user_trail
import json
from structlog import get_logger

logger = get_logger(__name__)


# global variables
table_name = 'Rooms'


@staff_member_required
def add(request):
    if request.method == 'POST':
        if request.POST.get('pk'):
            instance = Table.objects.get(pk=int(request.POST.get('pk')))
            pricing = Pricing.objects.get(room__pk=int(request.POST.get('pk')))
        else:
            instance = Table()
            pricing = Pricing()
        if request.POST.get('name'):
            instance.name = request.POST.get('name')
        if request.POST.get('price'):
            instance.price = request.POST.get('price')
        if request.POST.get('floor'):
            instance.floor = request.POST.get('floor')
        if request.POST.get('description'):
            instance.description = request.POST.get('description')
        if request.POST.get('is_booked'):
            b = lambda x: True if x > 0 else False
            instance.is_booked = b(int(request.POST.get('is_booked')))
        instance.save()
        # add amenities
        if request.POST.get('amenities'):
            choices = json.loads(request.POST.get('amenities'))
            instance.amenities.clear()
            for choice in choices:
                instance.amenities.add(choice)
            instance.save()
        # add price packages
        pricing.room = instance
        if request.POST.get('daily'):
            pricing.daily = request.POST.get('daily')
        if request.POST.get('nightly'):
            pricing.nightly = request.POST.get('nightly')
        if request.POST.get('daytime'):
            pricing.daytime = request.POST.get('daytime')
        if request.POST.get('weekly'):
            print request.POST.get('weekly')
            pricing.weekly = request.POST.get('weekly')
        if request.POST.get('monthly'):
            pricing.monthly = request.POST.get('monthly')
        pricing.save()

        edit_url = reverse(
            'dashboard:room-edit', kwargs={'pk': instance.pk})
        data = {'name': instance.name,
                'is_booked': instance.is_booked,
                'pk': instance.pk,
                'edit_url': edit_url}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        packages = Package.objects.all()
        package_json = []
        for package in packages:
            package_json.append({'name': str(package.name)})
        ctx = {'n': range(SiteSettings.objects.get(pk=1).floors), 'table_name': table_name, 'packages': packages, 'package_json': package_json}
        return TemplateResponse(request, 'dashboard/room/form.html', ctx)


@staff_member_required
def add_image(request, pk=None):
    if request.method == 'POST' and request.FILES['images[]'] and pk:
        try:
            instance = Table.objects.get(pk=pk)
            image = RoomImage()
            image.room = instance
            image.image = request.FILES['images[]']
            image.save()
            return HttpResponse('Image uploaded')
        except Exception as e:
            return HttpResponse('Image upload failed')
    else:
        return HttpResponse('no image')


@staff_member_required
def delete_image(request, pk=None):
    if request.method == 'POST' and pk:
        #instance = RoomImage.objects.all().delete()
        instance = RoomImage.objects.get(pk=pk)

        # Deletes Image Renditions
        instance.image.delete_all_created_images()
        # Deletes Original Image
        instance.image.delete()
        instance.delete()
        return HttpResponse('deleted successfully')
    else:
        return HttpResponse('Invalid method or PK')


@staff_member_required
def add_amenities(request):
    if request.method == 'POST':
        if request.POST.get('amenities'):
            choices = json.loads(request.POST.get('amenities'))
            for choice in choices:
                try:
                    RoomAmenity.objects.create(name=choice)
                except Exception as e:
                    logger.info(e)
            return HttpResponse(json.dumps({'success': choice}), content_type='application/json')
        return HttpResponse(json.dumps({'message': 'Amenities required'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'message', 'Invalid method'}))


@staff_member_required
def clone(request, pk=None):
    if pk:
        obj = Table.objects.get(pk=pk)
        temp = []
        for amenity in obj.amenities.all():
            temp.append(amenity)
        print temp
        pricing = Pricing.objects.get(room__pk=pk)
        instance = int(obj.pk) + 2
        floor = obj.floor
        if request.POST.get('times'):
            for i in range(int(request.POST.get('times'))):
                obj.pk = None
                pricing.pk = None
                if floor == '0':
                    obj.name = 'G' + str(floor) + '-' + str(i) + str(instance)
                else:
                    obj.name = 'F'+str(floor) + '-' + str(i) + str(instance)
                obj.is_booked = False
                try:
                    obj.save()
                    pricing.room = obj
                    pricing.save()
                    for amenity in temp:
                        obj.amenities.add(amenity)
                except Exception as e:
                    pass

        return HttpResponse(json.dumps({'message': obj.name}), content_type='application/json')
    return HttpResponse('Invalid request')


@staff_member_required
def delete(request, pk=None):
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        try:
            option.delete()
            user_trail(request.user.name, 'deleted room : '+ str(option.name), 'delete')
            logger.info('deleted room: '+ str(option.name))
            return HttpResponse('success')
        except Exception, e:
            logger.error(e)
            return HttpResponse(e)


@staff_member_required
def detail(request, pk=None):
    if request.method == 'GET':
        try:
            room = get_object_or_404(Table, pk=pk)
            book = Book.objects.filter(room__pk=pk).first()
            history = BookingHistory.objects.filter(room__pk=pk)
            ctx = {'room': room, 'book': book, 'history': history}
            return TemplateResponse(request, 'dashboard/room/detail.html', ctx)
        except Exception, e:
            logger.error(e)
            return TemplateResponse(request, 'dashboard/room/detail.html', {'error': e})


@staff_member_required
def edit(request, pk=None):
    room = get_object_or_404(Table, pk=pk)
    pricing = Pricing.objects.get(room__pk=room.pk)
    if request.method == 'GET':
        ctx = {'table_name': table_name, 'room': room, 'pricing': pricing}
        return TemplateResponse(request, 'dashboard/room/form.html', ctx)
    if request.method == 'POST':
        try:
            if request.POST.get('name'):
                room.name = request.POST.get('name')
            if request.POST.get('price'):
                room.number = request.POST.get('price')
                room.save()
                user_trail(request.user.name, 'updated room : '+ str(room.name),'edit')
                logger.info('updated room : '+ str(room.name))
                return HttpResponse('success')
            else:
                return HttpResponse('invalid response')
        except Exception, e:
            logger.error(e)
            print e
            return HttpResponse(e)


@staff_member_required
def fetch_amenities(request):
    search = request.GET.get('search')
    amenities = RoomAmenity.objects.all().filter(name__icontains=str(search))
    l = []
    for amenity in amenities:
        # {"text": "Afghanistan", "value": "AF"},
        contact = {'text': amenity.name, 'value': amenity.id}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')


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
        logger.info('User: ' + str(request.user.name) + 'accessed '+table_name+' List Page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/room/list.html', data)
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing payment options')


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
            return TemplateResponse(request,'dashboard/room/paginate.html',{'options':options})

        if list_sz:
            paginator = Paginator(options, int(list_sz))
            options = paginator.page(page)
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': request.GET.get('gid')}
            return TemplateResponse(request, 'dashboard/room/p2.html',data)

        paginator = Paginator(options, 10)
        options = paginator.page(page)
        data = {'options': options,
                'pn': paginator.num_pages,
                'sz': 10,
                'gid': request.GET.get('gid')}
        return TemplateResponse(request,'dashboard/room/p2.html', data)
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
                return TemplateResponse(request, 'dashboard/room/p2.html', data)
            else:
                paginator = Paginator(options, 10)
            if p2_sz:
                paginator = Paginator(options, int(p2_sz))
                options = paginator.page(page)
                data = {
                    "options": options
                }
                return TemplateResponse(request, 'dashboard/room/paginate.html', data)

            try:
                options = paginator.page(page)
            except PageNotAnInteger:
                options = paginator.page(1)
            except InvalidPage:
                options = paginator.page(1)
            except EmptyPage:
                options = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/room/paginate.html', {"options": options})
        except Exception, e:
            return HttpResponse()


@staff_member_required
def room_image_edit(request, room_pk, img_pk=None):
    room = get_object_or_404(Table, pk=room_pk)
    if img_pk:
        room_image = get_object_or_404(room.images, pk=img_pk)
    else:
        room_image = RoomImage(room=room)
    show_variants = room.room_class.has_variants
    form = RoomImageForm(request.POST or None, request.FILES or None, instance=room_image)
    if form.is_valid():
        room_image = form.save()
        if img_pk:
            msg = pgettext_lazy(
                'Dashboard message',
                'Updated image %s') % room_image.image.name
        else:
            msg = pgettext_lazy(
                'Dashboard message',
                'Added image %s') % room_image.image.name
        messages.success(request, msg)
        success_url = request.POST['success_url']
        if is_safe_url(success_url, request.get_host()):
            return redirect(success_url)
    ctx = {'form': form, 'room': room, 'product_image': room_image,
           'show_variants': show_variants}
    if request.GET.get('url'):
        ctx['post_url'] = request.GET.get('url')
    if request.is_ajax():
        return TemplateResponse(request, 'dashboard/product/partials/product_image_form.html', ctx)

    return TemplateResponse(
        request, 'dashboard/product/product_image_form.html', ctx)


@staff_member_required
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
                return TemplateResponse(request, 'dashboard/room/paginate.html', {'options': options,'sz':sz})
            data = {'options': options,
                    'pn': paginator.num_pages,
                    'sz': sz,
                    'q': q}
            return TemplateResponse(request, 'dashboard/room/search.html', data)

