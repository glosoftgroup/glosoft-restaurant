from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q

from ..dashboard.views import staff_member_required
from ..userprofile.models import User
from ..decorators import user_trail
from .models import ExpenseType, PersonalExpenses
from structlog import get_logger

logger = get_logger(__name__)


def expenses(request):
    try:
        expenses = PersonalExpenses.objects.all().order_by('-id')
        expense_types = ExpenseType.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(expenses, 10)
        try:
            expenses = paginator.page(page)
        except PageNotAnInteger:
            expenses = paginator.page(1)
        except InvalidPage:
            expenses = paginator.page(1)
        except EmptyPage:
            expenses = paginator.page(paginator.num_pages)
        data = {
            "expenses": expenses,
            "expense_types": expense_types
        }
        user_trail(request.user.name, 'accessed expenses', 'views')
        logger.info('User: ' + str(request.user.name) + 'accessed expenses page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/accounts/personal_expenses/list.html', data)
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing users')


@staff_member_required
def expenses_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    if request.GET.get('gid'):
        type = ExpenseType.objects.get(pk=request.GET.get('gid'))
        expenses = PersonalExpenses.objects.filter(expense_type=type.name)
        if p2_sz:
            paginator = Paginator(expenses, int(p2_sz))
            expenses = paginator.page(page)
            return TemplateResponse(request, 'dashboard/accounts/personal_expenses/paginate.html',
                                    {'expenses': expenses})

        paginator = Paginator(expenses, 10)
        expenses = paginator.page(page)
        return TemplateResponse(request, 'dashboard/accounts/personal_expenses/p2.html',
                                {'expenses': expenses, 'pn': paginator.num_pages, 'sz': 10,
                                 'gid': request.GET.get('gid')})
    else:
        try:
            expenses = PersonalExpenses.objects.all().order_by('-id')
            if list_sz:
                paginator = Paginator(expenses, int(list_sz))
                expenses = paginator.page(page)
                data = {
                    'expenses': expenses,
                    'pn': paginator.num_pages,
                    'sz': list_sz,
                    'gid': 0
                }
                return TemplateResponse(request, 'dashboard/accounts/personal_expenses/p2.html', data)
            else:
                paginator = Paginator(expenses, 10)
            if p2_sz:
                paginator = Paginator(expenses, int(p2_sz))
                expenses = paginator.page(page)
                data = {
                    "expenses": expenses
                }
                return TemplateResponse(request, 'dashboard/accounts/personal_expenses/paginate.html', data)

            try:
                expenses = paginator.page(page)
            except PageNotAnInteger:
                expenses = paginator.page(1)
            except InvalidPage:
                expenses = paginator.page(1)
            except EmptyPage:
                expenses = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/accounts/personal_expenses/paginate.html',
                                    {"expenses": expenses})
        except Exception, e:
            return HttpResponse()


def detail(request):
    status = 'read'
    return TemplateResponse(request, 'dashboard/accounts/personal_expenses/expenses.html', {})


def add(request):
    expense_types = ExpenseType.objects.all()
    staff = User.objects.all()
    data = {
        "expense_types": expense_types,
        "staff": staff
    }
    user_trail(request.user.name, 'viewed add expenses page', 'view')
    logger.info('User: ' + str(request.user.name) + 'viewed add expenses page')
    return TemplateResponse(request, 'dashboard/accounts/personal_expenses/expenses.html', data)


def add_process(request):
    voucher = request.POST.get('voucher')
    expense_type = request.POST.get('expense_type')
    expense_date = request.POST.get('expense_date')
    amount = request.POST.get('amount')
    authorized_by = request.POST.get('authorized_by')
    paid_to = request.POST.get('paid_to')
    received_by = request.POST.get('received_by')
    phone = request.POST.get('phone')
    description = request.POST.get('description')
    new_expense = PersonalExpenses(voucher=voucher, expense_type=expense_type, expense_date=expense_date,
                                   amount=amount, authorized_by=authorized_by, paid_to=paid_to,
                                   received_by=received_by, phone=phone,
                                   description=description)

    try:
        new_expense.save()
        user_trail(request.user.name, 'added an expense : ' + str(expense_type) + ' with amount:' + str(amount), 'add')
        logger.info('User: ' + str(request.user.name) + 'created expense type:' + str(expense_type))
        return HttpResponse('success')
    except Exception as e:
        logger.info('Error when saving ')
        logger.error('Error when saving ')
        return HttpResponse(e)


def edit(request, pk=None):
    return TemplateResponse(request, 'dashboard/accounts/personal_expenses/edit_expense.html', {})


def delete(request, pk=None):
    expense = get_object_or_404(PersonalExpenses, pk=pk)
    if request.method == 'POST':
        try:
            expense.delete()
            user_trail(request.user.name, 'deleted expense: ' + str(expense.expense_type), 'delete')
            logger.info('deleted expense: ' + str(expense.expense_type))
            return HttpResponse('success')
        except Exception, e:
            logger.error(e)
            return HttpResponse(e)


def expenses_search(request):
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
            expenses = PersonalExpenses.objects.filter(
                Q(expense_type__icontains=q) |
                Q(paid_to__icontains=q) | Q(received_by__icontains=q) |
                Q(phone__icontains=q)).order_by('id')
            paginator = Paginator(expenses, 10)
            try:
                expenses = paginator.page(page)
            except PageNotAnInteger:
                expenses = paginator.page(1)
            except InvalidPage:
                expenses = paginator.page(1)
            except EmptyPage:
                expenses = paginator.page(paginator.num_pages)
            if p2_sz:
                expenses = paginator.page(page)
                return TemplateResponse(request, 'dashboard/accounts/personal_expenses/paginate.html',
                                        {'expenses': expenses})

            return TemplateResponse(request, 'dashboard/accounts/personal_expenses/search.html',
                                    {'expenses': expenses, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


def detail(request, pk=None):
    if request.method == 'GET':
        try:
            expense = get_object_or_404(PersonalExpenses, pk=pk)
            user_trail(request.user.name, 'access expense details of: ' + str(expense.expense_type) + ' on ' + str(
                expense.expense_date), 'view')
            logger.info(
                'access expense details of: ' + str(expense.expense_type) + ' on ' + str(expense.expense_date))
            return TemplateResponse(request, 'dashboard/accounts/expenses/detail.html', {'expense': expense})
        except Exception, e:
            logger.error(e)
            return TemplateResponse(request, 'dashboard/accounts/expenses/detail.html', {'expense': expense})
