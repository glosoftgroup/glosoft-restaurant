import logging
import datetime
from django.db.models import Q, Sum
from django.http import HttpResponse
from .views import staff_member_required
from datetime import date
from .models import ExpenseType, Expenses, PettyCash
from saleor.utils import render_to_pdf, default_logo, image64

error_logger = logging.getLogger('error_logger')


@staff_member_required
def pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        type = None
        if q is not None:
            expenses = Expenses.objects.filter(
                Q(expense_type__icontains=q) |
                Q(paid_to__icontains=q) | Q(authorized_by__icontains=q)).order_by('id')

            if gid:
                type = ExpenseType.objects.get(pk=request.GET.get('gid'))
                expenses = expenses.filter(expense_type=type.name)

        elif gid:
            type = ExpenseType.objects.get(pk=request.GET.get('gid'))
            expenses = Expenses.objects.filter(expense_type=type.name)
        else:
            expenses = Expenses.objects.all()
        img = image64()
        data = {
            'today': date.today(),
            'expenses': expenses,
            'puller': request.user,
            'image': img,
            'type': type
        }
        pdf = render_to_pdf('dashboard/accounts/expenses/pdf/expenses.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


def pettycash_detail_pdf(request, pk=None):
    try:
        pettycash  =PettyCash.objects.get(pk=pk)
        date = pettycash.created.date().strftime('%Y-%m-%d')

        expenses = Expenses.objects.filter(added_on__icontains=date)
        if expenses:
            expenses = expenses
            total_expenses = expenses.aggregate(Sum('amount'))['amount__sum']
        else:
            expenses = []
            total_expenses = 0


        img = default_logo()
        data = {
            'today': datetime.date.today(),
            'expenses': expenses,
            'pettycash': pettycash,
            'puller': request.user,
            'image': img,
            'total_expenses': total_expenses
        }
        pdf = render_to_pdf('petty_cash/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except Exception as e:
        error_logger.error(e)
