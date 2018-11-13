from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.utils.translation import pgettext_lazy
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, Q
from django.db import IntegrityError

from ..views import staff_member_required
from ...customer.models import Customer, AddressBook
from ...sale.models import (Sales, SoldItem)
from ...credit.models import Credit
from ...decorators import permission_decorator, user_trail
from saleor.booking.models import Book, RentPayment
from saleor.room.models import Maintenance
import json
import random

from structlog import get_logger

logger = get_logger(__name__)

table_name = 'Customers'


@staff_member_required
@permission_decorator('customer.view_customer')
def users(request):
    global table_name

    ctx = {'table_name': table_name}
    return TemplateResponse(request, 'dashboard/customer/users.html', ctx)


@staff_member_required
@permission_decorator('customer.add_customer')
def user_add(request):
    try:
        user_trail(request.user.name, 'accessed add customer page', 'view')
        logger.info('User: ' + str(request.user.name) + 'accessed add customer page')
        return TemplateResponse(request, 'dashboard/customer/add.html',{'permissions':"permissions", 'groups':"groups"})
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing add users page')

@staff_member_required
def user_process(request):
    user = Customer.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        nid = request.POST.get('nid')
        nationality = request.POST.get('nationality')
        mobile = request.POST.get('mobile')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        new_user = Customer.objects.create(
            name=name,
            email=email,
            nid=nid,
            nationality=nationality,
            mobile=mobile,
            image=image,
            description=description
        )
        try:
            new_user.save()
            user_trail(request.user.name, 'created customer: ' + str(name), 'add')
            logger.info('User: ' + str(request.user.name) + ' created customer:' + str(name))

            success_url = reverse(
                'dashboard:customer-edit', kwargs={'pk': new_user.pk})
            data = {'success_url': success_url, 'message':'Tenant added successfully','status':'success'}
        except IntegrityError as e:
            data = {'success_url': None, 'message':'Tenant with that mobile already exists', 'status':'error'}
        except Exception as e:
            data = {'success_url': None, 'message':'Error encountered when adding Tenant'+str(e), 'status':'error'}
            logger.info('Error when saving ')

        return HttpResponse(json.dumps(data), content_type='application/json')


def user_detail(request, pk):
    try:
        user = Customer.objects.get(pk=pk)
        try:
            booking = Book.objects.get(customer__pk=user.pk, active=True, room__is_booked=True)
            room = Book.objects.get(customer=user, active=True).room
            balance_with_charges = booking.balance_with_charges.gross + booking.service_charges.gross
        except:
            booking = None
            room = None
            balance_with_charges = 0

        ctx = {'user': user, 'table_name': 
                'Customer', 'room':room, 'booking':booking, 
                'balance_with_charges':balance_with_charges}
        user_trail(request.user.name, 'accessed detail page to view customer: ' + str(user.name), 'view')
        logger.info('User: ' + str(request.user.name) + ' accessed detail page to view customer:' + str(user.name))
        return TemplateResponse(request, 'dashboard/customer/detail.html', ctx)
    except:
        print ('*')*100
        return TemplateResponse(request, 'dashboard/customer/detail.html', {})


def sales_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    try:
        all_sales = Sales.objects.filter(customer=customer)
        total_sales_amount = all_sales.aggregate(Sum('total_net'))
        total_tax_amount = all_sales.aggregate(Sum('total_tax'))
        total_sales = []
        for sale in all_sales:
            quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
            setattr(sale, 'quantity', quantity['c'])
            total_sales.append(sale)

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
        user_trail(request.user.name, 'accessed sales details for customer'+str(customer.name), 'view')
        logger.info('User: ' + str(request.user.name) + 'accessed sales details for customer'+str(customer.name))
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            data = {
                'sales': total_sales,
                "total_sales_amount":total_sales_amount,
                "total_tax_amount":total_tax_amount,
                "customer":customer,
                'pn': paginator.num_pages
            }
            return TemplateResponse(request, 'dashboard/customer/sales/sales_list.html',data)
    except ObjectDoesNotExist as e:
        logger.error(e)

def sales_items_detail(request, pk=None, ck=None):
    try:
        customer = get_object_or_404(Customer, pk=ck)
        sale = Sales.objects.get(pk=pk)
        items = SoldItem.objects.filter(sales=sale)
        return TemplateResponse(request, 'dashboard/customer/sales/details.html',{'items': items, "sale":sale, "customer":customer})
    except ObjectDoesNotExist as e:
        logger.error(e)


@permission_decorator('customer.delete_customer')
def user_delete(request, pk):
    global table_name
    user = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        user.delete()
        user_trail(request.user.name, 'deleted customer: ' + str(user.name))
        ctx = {'table_name': table_name}
        return TemplateResponse(request, 'dashboard/customer/users.html', ctx)


@permission_decorator('customer.change_customer')
def user_edit(request, pk):
    user = get_object_or_404(Customer, pk=pk)
    ctx = {'user': user}
    user_trail(request.user.name, 'accessed edit page for customer '+ str(user.name),'update')
    logger.info('User: '+str(request.user.name)+' accessed edit page for customer: '+str(user.name))
    return TemplateResponse(request, 'dashboard/customer/edit.html', ctx)

def user_update(request, pk):
    user = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        nid = request.POST.get('nid')
        nationality = request.POST.get('nationality')
        mobile = request.POST.get('mobile')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        if image:
            user.image = image

        user.name = name
        user.email = email
        user.nid = nid
        user.nationality = nationality
        user.mobile = mobile
        user.description = description
        user.save()
        user_trail(request.user.name, 'updated customer: ' + str(user.name))
        logger.info('User: ' + str(request.user.name) + ' updated supplier: ' + str(user.name))
        return HttpResponse("success without image")


@staff_member_required
def customer_pagination(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    users = Customer.objects.all().order_by('-id')
    if list_sz:
        paginator = Paginator(users, int(list_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/customer/pagination/p2.html',
                                {'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
    else:
        paginator = Paginator(users, 10)
    if p2_sz:
        paginator = Paginator(users, int(p2_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/customer/pagination/paginate.html', {"users":users})

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except InvalidPage:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'dashboard/customer/pagination/paginate.html', {"users":users})

@staff_member_required
def customer_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz == 0:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            queryset_list = Customer.objects.filter(
                Q(name__icontains=q)|
                Q(email__icontains=q) |
                Q(mobile__icontains=q)
            ).order_by('-id')
            paginator = Paginator(queryset_list, 10)

            try:
                queryset_list = paginator.page(page)
            except PageNotAnInteger:
                queryset_list = paginator.page(1)
            except InvalidPage:
                queryset_list = paginator.page(1)
            except EmptyPage:
                queryset_list = paginator.page(paginator.num_pages)
            users = queryset_list
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/pagination/paginate.html', {"users":users})

            return TemplateResponse(request, 'dashboard/customer/pagination/search.html',
            {"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def is_creditable(request):
    if request.method == "POST":
        if request.POST.get('pk'):
            customer = Customer.objects.get(pk=int(request.POST.get("pk")))
            if request.POST.get('is_creditable'):
                if int(request.POST.get('is_creditable')) == 1:
                    customer.creditable = True;
                if int(request.POST.get('is_creditable')) == 0:
                    customer.creditable = False;
                customer.save()
            return HttpResponse(json.dumps({'success':customer.creditable}),content_type='application/json')
    else:
        return HttpResponse(json.dumps({'error':'Invalid method GET'}),content_type='applicatoin/json')

# reports
@staff_member_required
@permission_decorator('customer.view_customer')
def customer_report(request):
    try:
        users = Customer.objects.all().order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed customers page', 'view')
        logger.info('User: ' + str(request.user.name) + 'view customers')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/customer/reports/list.html',{'users': users, 'pn': paginator.num_pages})
    except TypeError as e:
        logger.error(e)
        return TemplateResponse(request, 'dashboard/customer/reports/list.html', {'users': users, 'pn': paginator.num_pages})

@staff_member_required
def report_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz == 0:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            queryset_list = Customer.objects.filter(
                Q(name__icontains=q)|
                Q(email__icontains=q) |
                Q(mobile__icontains=q)
            ).order_by('-id')
            paginator = Paginator(queryset_list, 10)

            try:
                queryset_list = paginator.page(page)
            except PageNotAnInteger:
                queryset_list = paginator.page(1)
            except InvalidPage:
                queryset_list = paginator.page(1)
            except EmptyPage:
                queryset_list = paginator.page(paginator.num_pages)
            users = queryset_list
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/pagination/report_paginate.html', {"users":users})

            return TemplateResponse(request, 'dashboard/customer/pagination/report_search.html',
            {"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
def report_pagination(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    users = Customer.objects.all().order_by('-id')
    if list_sz:
        paginator = Paginator(users, int(list_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/customer/pagination/report_p2.html',
                                {'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
    else:
        paginator = Paginator(users, 10)
    if p2_sz:
        paginator = Paginator(users, int(p2_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/customer/pagination/report_paginate.html', {"users":users})

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except InvalidPage:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'dashboard/customer/pagination/report_paginate.html', {"users":users})

# credit views
@staff_member_required
@permission_decorator('customer.view_customer')
def credit_report(request):
    try:
        users =  Credit.objects.filter(~Q(customer=None)).order_by('-id')
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed customers page', 'view')
        logger.info('User: ' + str(request.user.name) + 'view customers')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/customer/credit/list.html',{'users': users, 'pn': paginator.num_pages})
    except TypeError as e:
        logger.error(e)
        return TemplateResponse(request, 'dashboard/customer/credit/list.html', {'users': users, 'pn': paginator.num_pages})

@staff_member_required
def credit_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size', 10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz == 0:
            sz = 10
        else:
            sz = list_sz
        if q is not None:
            queryset_list = Credit.objects.filter(~Q(customer=None)).filter(
                Q(customer__name__icontains=q)|
                Q(customer__email__icontains=q) |
                Q(customer__mobile__icontains=q)
            ).order_by('-id')
            paginator = Paginator(queryset_list, 10)

            try:
                queryset_list = paginator.page(page)
            except PageNotAnInteger:
                queryset_list = paginator.page(1)
            except InvalidPage:
                queryset_list = paginator.page(1)
            except EmptyPage:
                queryset_list = paginator.page(paginator.num_pages)
            users = queryset_list
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/customer/pagination/credit_paginate.html', {"users":users})

            return TemplateResponse(request, 'dashboard/customer/pagination/credit_search.html',
            {"users":users, 'pn': paginator.num_pages, 'sz': sz, 'q': q})

@staff_member_required
def credit_pagination(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    users = Credit.objects.filter(~Q(customer=None)).order_by('-id')
    if list_sz:
        paginator = Paginator(users, int(list_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/customer/pagination/credit_p2.html',
                                {'users':users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0})
    else:
        paginator = Paginator(users, 10)
    if p2_sz:
        paginator = Paginator(users, int(p2_sz))
        users = paginator.page(page)
        return TemplateResponse(request, 'dashboard/customer/pagination/credit_paginate.html', {"users":users})

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except InvalidPage:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'dashboard/customer/pagination/credit_paginate.html', {"users":users})



@staff_member_required
def add_dependency(request, pk):
    if request.is_ajax():
        if request.method == 'GET':
            if pk:
                pk = pk
            ctx = {'customer_pk': pk}
            return TemplateResponse(request, 'dashboard/customer/_address_add.html', ctx)
        if request.method == 'POST':
            name = request.POST.get('name')
            id_no = request.POST.get('id_no')
            nationality = request.POST.get('nationality')
            phone = request.POST.get('phone').replace('(', '').replace(')', '').replace('-', '')
            maturity_status = request.POST.get('maturity_status')
            relation = request.POST.get('relation')
            supplier = get_object_or_404(Customer, pk=pk)
            address = AddressBook.objects.create(
                name=name,
                id_no=id_no,
                phone=phone,
                nationality=nationality,
                maturity_status=maturity_status,
                relation=relation
            )
            address.save()

            supplier.addresses.add(address)

            ctx = {'address': address}
        return TemplateResponse(request,
                                'dashboard/customer/_newContact.html',
                                ctx)

@staff_member_required
def refresh_dependency(request, pk=None):
    if request.method == 'GET':
        if pk:
            user = get_object_or_404(Customer, pk=pk)
            ctx = {'user': user}
            return TemplateResponse(request,
                                    'dashboard/customer/_newContact.html',
                                    ctx)
    return HttpResponse('Post request not accepted')


@staff_member_required
def dependency_delete(request, pk):
    address = get_object_or_404(AddressBook, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(
            request,
            pgettext_lazy(
                'Dashboard message', 'Deleted Dependency %s') % address)
        if pk:
            if request.is_ajax():
                script = "'#tr" + str(pk) + "'"
                return HttpResponse(script)
    ctx = {'address': address}
    return TemplateResponse(request,
                            'dashboard/customer/modal_delete.html',
                            ctx)

@staff_member_required
def pay(request, pk=None):
    try:
        customer = Customer.objects.get(pk=pk)
    except:
        customer = none

    # create payment instance
    if request.method == 'POST':
        instance = RentPayment()
        try:
            instance.invoice_number = 'inv/fx/0'+str(RentPayment.objects.latest('id').id)
            instance.invoice_number += ''.join(random.choice('0123456789ABCDEF') for i in range(4))
        except Exception as e:
            instance.invoice_number = 'inv/fx/1'+''.join(random.choice('0123456789ABCDEF') for i in range(4))

        instance.customer = customer
        if request.POST.get('date_paid'):
            instance.date_paid = request.POST.get('date_paid')
        if request.POST.get('amount_paid'):
            instance.amount_paid = request.POST.get('amount_paid')
        print instance.amount_paid

        book = Book.objects.get(customer__pk=customer.pk, active=True, room__is_booked=True)
        instance.room = book.room

        try:
            book = Book.objects.get(customer__pk=customer.pk, active=True, room__is_booked=True)
            instance.room = book.room
            book_amount = book.amount_paid.gross
            book_balance = book.balance.gross
            if  book_amount== 0:
                try:
                    instance.total_amount = book_balance
                    # add all the amount paid so far
                    book.amount_paid = book_amount + instance.amount_paid.gross
                    # calculate the balance
                    bookBalance = book_balance - instance.amount_paid.gross
                    book.balance = bookBalance
                    #calculate the balance with the charges
                    book.balance_with_charges = bookBalance + book.service_charges.gross + book.room.service_charges
                    #record the balance and the service charges in the RentPayment model
                    instance.balance = bookBalance
                    instance.service_charges = book.service_charges.gross + book.room.service_charges
                    book.service_charges = 0
                    instance.total_balance = instance.service_charges.gross + instance.balance.gross
                    instance.save()
                    book.save()
                except Exception as e:
                    print (e)
            else:
                try:
                    #total amount remaining
                    instance.total_amount = book.balance_with_charges.gross
                    #the total amount paid
                    book.amount_paid = book_amount + instance.amount_paid.gross
                    #calculate the balance with the charges
                    bookBalanceWitharges = book.balance_with_charges.gross - instance.amount_paid.gross
                    book.balance_with_charges = bookBalanceWitharges
                    # calculate the balance without the charges
                    bookBalance = book_balance - instance.amount_paid.gross
                    book.balance = bookBalance
                    # assign the total to the to the payment instance
                    instance.balance = bookBalanceWitharges
                    instance.service_charges = book.service_charges.gross + book.room.service_charges
                    instance.total_balance = instance.service_charges.gross + instance.balance.gross

                    book.balance_with_charges = bookBalanceWitharges + book.service_charges.gross + book.room.service_charges
                    book.service_charges = 0
                    instance.save()
                    book.save()
                except Exception as e:
                    print (e)

            data = {'success': 'success'}
            return HttpResponse(json.dumps(data), content_type='application/json')

        except Exception as e:
            print e
            return HttpResponse('Invalid request method')
        return HttpResponse('Invalid request method')

    return HttpResponse('Invalid request method')

@staff_member_required
def payments(request):
    global table_name

    ctx = {'table_name': table_name}
    return TemplateResponse(request, 'dashboard/customer/reports/payments.html', ctx)

@staff_member_required
def booking_invoice(request, pk=None):
    if request.method == 'GET':
        customer = None
        instance = get_object_or_404(Book, pk=pk)
        if not instance.invoice_number:
            try:
                instance.invoice_number = 'inv/fx/0'+str(Book.objects.latest('id').id)
                instance.invoice_number += ''.join(random.choice('0123456789ABCDEF') for i in range(4))
            except Exception as e:
                instance.invoice_number = 'inv/fx/1'+''.join(random.choice('0123456789ABCDEF') for i in range(4))
            instance.save()

        total_balance = instance.balance.gross + instance.service_charges.gross
        try:
            maintenance = Maintenance.objects.filter(
                room__pk=instance.room.pk,
                cost=instance.service_charges.gross).last()
            reason = maintenance.issue
        except:
            reason = None

        ctx = {'table_name': table_name, 'instance': instance, 'reason':reason,
            'customer':instance.customer, 'total_balance':total_balance}
        return TemplateResponse(request, 'dashboard/customer/reports/invoice.html', ctx)