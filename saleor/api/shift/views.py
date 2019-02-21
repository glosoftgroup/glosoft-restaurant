from rest_framework.response import Response
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.timezone import utc
from rest_framework import serializers
from ...userprofile.models import User
from rest_framework.decorators import api_view
from datetime import datetime, date, timedelta
from structlog import get_logger
from saleor.shift.models import Shift
from saleor.main_shift.models import MainShift
from saleor.sale.models import Terminal
from saleor.utils import is_shift_started


from .serializers import ShiftSerializer

logger = get_logger(__name__)


@api_view(['GET', 'POST', ])
def start_shift(request):

    cash_drawer_amount = "0.0"
    qs = Terminal.objects.all()
    if qs.last():
        cash_drawer_amount = str(qs.last().amount)

    if request.method == 'POST':

        code = request.data.get('code')
        email = request.data.get('email')
        note = request.data.get('note')
        balance = request.data.get('balance')
        main_shift_status = request.data.get('main_shift_status')

        """ if the main status is True then check if shift already exists, else create one if not """
        if bool(main_shift_status):
            if not is_shift_started():
                date_now = timezone.localtime(timezone.now())
                print(" -- now -- ")
                print(date_now)
                print(" -- now -- ")
                open_time_from_now = date_now
                close_date = date_now + timedelta(days=1)
                close_time = close_date.replace(hour=6, minute=0, second=0)
                close_time_from_now = close_time

                main_shift = MainShift()
                main_shift.opening_time = open_time_from_now
                main_shift.closing_time = close_time_from_now
                main_shift.save()

        if code and email:

            is_started_shift = True

            try:
                user = User.objects.get(code=code, email=email)

                now = datetime.now()
                time_now = now.strftime("%Y-%m-%d %H:%M: %p")
                date_today = now.strftime("%Y-%m-%d")

                query = Shift.objects.filter(created_at__icontains=date_today, user=user)

                if query.exists():
                    last = query.last()
                    if last.end_time:
                        shift = Shift.objects.create(
                            start_time=time_now, user=user,
                            start_counter_balance=cash_drawer_amount,
                            cashier_start_balance=balance,
                            start_note=note)
                else:
                    Shift.objects.create(
                        start_time=time_now, user=user,
                        start_counter_balance=cash_drawer_amount,
                        cashier_start_balance=balance,
                        start_note=note)

            except Exception as e:
                logger.error("check_shift_started", message=e.message)

                raise serializers.ValidationError(_('No such user exists.'))

            is_started_shift = {"is_started_shift": is_started_shift}

            serializer = ShiftSerializer(is_started_shift)

            return Response(serializer.data)

    raise serializers.ValidationError(_('Method not allowed'))


@api_view(['GET', 'POST', ])
def end_shift(request):
    cash_drawer_amount = "0.0"
    qs = Terminal.objects.all()
    if qs.last():
        cash_drawer_amount = str(qs.last().amount)

    if request.method == 'POST':

        code = request.data.get('code')
        email = request.data.get('email')
        note = request.data.get('note')
        balance = request.data.get('balance')
        main_shift_status = request.data.get('main_shift_status')

        """ if the main status is True then check if shift already exists and close it """
        if bool(main_shift_status):
            if is_shift_started():
                close_time_from_now = timezone.localtime(timezone.now())
                main_shift = MainShift.objects.all().last()
                main_shift.closing_time = close_time_from_now
                main_shift.save()

        if code and email:

            is_started_shift = False

            try:

                user = User.objects.get(code=code, email=email)

                now = datetime.now()
                time_now = now.strftime("%Y-%m-%d %H:%M: %p")

                query = Shift.objects.filter(user=user)
                if query.exists():
                    shift = query.last()
                    shift.end_time = time_now
                    shift.end_counter_balance = cash_drawer_amount
                    shift.cashier_end_balance = balance
                    shift.end_note = note
                    shift.save()

            except Exception as e:
                logger.error("check_shift_started", message=e.message)
                raise serializers.ValidationError(_('No such user exists.'))

            is_started_shift = {"is_started_shift": is_started_shift}

            serializer = ShiftSerializer(is_started_shift)

            return Response(serializer.data)

    raise serializers.ValidationError(_('Method not allowed'))
