from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.dateformat import DateFormat

from ..views import staff_member_required
from saleor.booking.models import Book as Table
from saleor.booking.models import Payment, BookingHistory
from saleor.room.models import Room
from saleor.customer.models import Customer
from saleor.sale.models import PaymentOption
from saleor.wing.models import Wing

from decimal import Decimal
import random
import json

from structlog import get_logger

logger = get_logger(__name__)

# global variables
table_name = 'Booking'


@staff_member_required
def add(request):
    global table_name
    if request.method == 'POST':
        if request.POST.get('pk'):
            instance = Table.objects.get(pk=request.POST.get('pk'))
            try:
                history = BookingHistory.objects.get(book__pk=int(request.POST.get('pk')))
            except Exception as e:
                print e
                history = BookingHistory()
        else:
            instance = Table()
            history = BookingHistory()
            try:
                instance.invoice_number = 'inv/bk/0' + str(Table.objects.latest('id').id)
                instance.invoice_number += ''.join(random.choice('0123456789ABCDEF') for i in range(4))
            except Exception as e:
                instance.invoice_number = 'inv/bk/1' + ''.join(random.choice('0123456789ABCDEF') for i in range(4))
            history.invoice_number = instance.invoice_number
        if request.POST.get('c_name'):
            customer_name = request.POST.get('c_name')
        if request.POST.get('mobile'):
            mobile = request.POST.get('mobile')
        try:
            customer = Customer.objects.get(mobile=mobile)
        except:
            try:
                customer = Customer.objects.create(name=customer_name, mobile=mobile)
            except:
                pass
        try:
            instance.customer = customer
        except:
            pass
        try:
            history.customer = customer
        except:
            pass
        if request.POST.get('total_price'):
            instance.price = request.POST.get('total_price')
            history.price = request.POST.get('total_price')
        if request.POST.get('amount_paid'):
            instance.amount_paid = request.POST.get('amount_paid')
        if request.POST.get('check_in'):
            instance.check_in = request.POST.get('check_in')
            history.check_in = request.POST.get('check_in')
        if request.POST.get('price_type'):
            instance.price_type = request.POST.get('price_type')
        if request.POST.get('check_out'):
            instance.check_out = request.POST.get('check_out')
            history.check_out = request.POST.get('check_out')
        if request.POST.get('days'):
            instance.days = request.POST.get('days')
        if request.POST.get('child'):
            instance.child = request.POST.get('child')
        if request.POST.get('adult'):
            instance.adult = request.POST.get('adult')
        if request.POST.get('description'):
            instance.description = request.POST.get('description')
        if request.POST.get('active'):
            b = lambda x: True if x > 0 else False
            instance.active = b(int(request.POST.get('active')))
        instance.user = request.user
        instance.save()
        if request.POST.get('room_id'):
            try:
                room = Room.objects.get(pk=int(request.POST.get('room_id')))
                instance.room = room
                history.room = room
                room.is_booked = True
                room.available_on = request.POST.get("check_out")
                room.save()
            except Exception as e:
                return HttpResponse(json.dumps({'error': str(e)}), content_type="application/json")
        # compute balance
        instance.balance = instance.price.gross - instance.amount_paid.gross
        instance.save()
        history.save()

        data = {
            'name': instance.room.name,
            'active': instance.active,
            'room_pk': instance.room.id
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
        # return HttpResponse(json.dumps({'message': 'Invalid method'}))
    else:
        ctx = {'table_name': table_name}
        if request.GET.get("room_pk"):
            room = Room.objects.get(pk=int(request.GET.get("room_pk")))
            ctx['room'] = room
        if request.is_ajax():
            return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/modal_form.html', ctx)
        return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/form.html', ctx)


@staff_member_required
def book(request):
    global table_name
    objects = Room.objects.all().order_by('floor')
    floors = []
    for floor in objects:
        if floor.room_wing not in floors:
            floors.append(floor.room_wing)
    number_of_floors = len(floors)
    wings = Wing.objects.all()
    active = wings.first()
    ctx = {
        'active': active,
        'table_name': table_name,
        'objects': objects,
        "floors": floors,
        "wings": wings,
        "number_of_floors": number_of_floors
    }
    return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/rooms.html', ctx)


@staff_member_required
def delete(request, pk=None):
    global table_name
    option = get_object_or_404(Table, pk=pk)
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            option.delete()
            data = {
                "table_name": table_name,
            }
            return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/list.html', data)
        except Exception, e:
            logger.error(e)
            return HttpResponse(e)


@staff_member_required
def detail(request, pk=None):
    global table_name
    if pk:
        payment_options = PaymentOption.objects.all()
        instance = Table.objects.filter(pk=pk).first()
        ctx = {'table_name': table_name, 'instance': instance, 'payment_options': payment_options}
        return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/detail.html', ctx)
    return HttpResponse('Invalid Request. Booking id required')


@staff_member_required
def edit(request, pk=None):
    global table_name
    instance = get_object_or_404(Table, pk=pk)
    if request.method == 'GET':
        ctx = {'table_name': table_name, 'instance': instance}
        return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/form.html', ctx)
    if request.method == 'POST':
        return HttpResponse('Invalid Request method')


@staff_member_required
def invoice(request, pk=None):
    global table_name
    if pk:
        payment_options = PaymentOption.objects.all()
        instance = Table.objects.filter(room__pk=pk).first()
        ctx = {
            'table_name': table_name,
            'instance': instance, 'payment_options': payment_options
        }
        return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/invoice.html', ctx)
    return HttpResponse('Invalid Request. Booking id required')


@staff_member_required
def listing(request):
    global table_name
    data = {
        "table_name": table_name,
    }
    return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/list.html', data)


@staff_member_required
def charts(request):
    global table_name
    data = {"table_name": table_name}
    if request.is_ajax():
        # get last 30 room bookings
        last_thirty_booking = Table.objects.all().order_by('id')[:30]
        last_visits_booking = []
        for obj in last_thirty_booking:
            last_visits_booking.append(
                {'date': DateFormat(obj.created).format('Y-m-d'),
                 'total': Table.objects.total_bookings(obj.created)})
        last_amount_booking = []
        for obj in last_thirty_booking:
            last_amount_booking.append(
                {'date': DateFormat(obj.created).format('Y-m-d'),
                 'total': Table.objects.total_bookings(obj.created, 'amount')})

        yearly_visits = Table.objects.yearly_visits_data()
        yearly_amount = Table.objects.yearly_amount_data()
        monthly = Table.objects.monthly_visits_data()
        return HttpResponse(
            json.dumps(
                {"results":
                     {'last_amount': last_amount_booking,
                      'last_visits': last_visits_booking,
                      'yearly_visits': yearly_visits,
                      'yearly_amount': yearly_amount,
                      "monthly": monthly}
                 }), content_type='application/json')
    return TemplateResponse(request, 'dashboard/' + table_name.lower() + '/charts.html', data)


@staff_member_required
def pay(request):
    global table_name
    # create instance
    instance = Payment()
    if request.method == 'POST':
        if request.POST.get('invoice_number'):
            instance.invoice_number = request.POST.get('invoice_number')
        if request.POST.get('book'):
            book = Table.objects.get(pk=int(request.POST.get('book')))
            instance.book = book
            instance.customer = book.customer
        if request.POST.get('amount_paid'):
            instance.amount_paid = request.POST.get('amount_paid')
        if request.POST.get('payment_option'):
            instance.payment_option = PaymentOption.objects.get(pk=int(request.POST.get('payment_option')))
        if request.POST.get('date'):
            instance.date = request.POST.get('date')
        if request.POST.get('description'):
            instance.description = request.POST.get('description')
        instance.save()
        book.amount_paid = book.amount_paid.gross + instance.amount_paid.gross
        book.balance = book.balance.gross - instance.amount_paid.gross
        book.save()
        data = {'balance': float(book.balance.gross),
                'total_paid': float(book.amount_paid.gross)}

        return HttpResponse(json.dumps(data), content_type='application/json')

    return HttpResponse('Invalid request method')


@staff_member_required
def fetch_amenities(request):
    global table_name
    search = request.GET.get('search')
    dictionary = Room.objects.all().exclude(is_booked=True).filter(name__icontains=str(search))
    l = []
    for instance in dictionary:
        # {"text": "Afghanistan", "value": "AF"},
        text = instance.name
        try:
            text = str(instance.name) + ' ' + str(instance.room_wing.name)
        except Exception as e:
            print(e)
        contact = {'text': text, 'value': instance.id}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')


@staff_member_required
def customer_token(request):
    global table_name
    if request.GET.get('customer'):
        pk = int(request.GET.get('customer'))
        instance = Customer.objects.get(pk=pk)
        l = []
        contact = {
            "results": {
                'text': instance.name,
                'value': instance.id,
                'mobile': instance.mobile
            }
        }
        l.append(contact)
        return HttpResponse(json.dumps(l[0]), content_type='application/json')
    search = request.GET.get('search')
    dictionary = Customer.objects.all().filter(name__icontains=str(search))
    l = []
    for instance in dictionary:
        # {"text": "Afghanistan", "value": "AF"},
        contact = {'text': instance.name, 'value': instance.id}
        l.append(contact)
    return HttpResponse(json.dumps(l), content_type='application/json')


@staff_member_required
def compute_room_price(request):
    global table_name
    days = int(request.POST.get('days'))
    price_type = request.POST.get('price_type')
    rooms = json.loads(request.POST.get('rooms'))
    total = Decimal(0)
    for instance in rooms:
        room = Room.objects.get(pk=int(instance))
        # total = float(total + eval('room.get_'+str(price_type)+'_price()'))
        print(room.price.gross)
        total = total + Decimal(room.price.gross)

    try:
        total *= Decimal(days)
    except:
        pass
    return HttpResponse(json.dumps({"price": float(total)}), content_type='application/json')
