from rest_framework.response import Response
from django.utils.translation import ugettext as _
from rest_framework import serializers
from ...userprofile.models import User
from rest_framework.decorators import api_view
from datetime import datetime
from structlog import get_logger
from saleor.shift.models import Shift


from .serializers import ShiftSerializer

logger = get_logger(__name__)


@api_view(['GET', 'POST', ])
def start_shift(request):

    if request.method == 'POST':

        code = request.data.get('code')
        email = request.data.get('email')
        note = request.data.get('note')

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
                        shift = Shift.objects.create(start_time=time_now, user=user,
                                             start_counter_balance="0.0", start_note=note)
                else:
                    Shift.objects.create(start_time=time_now, user=user,
                                         start_counter_balance="0.0", start_note=note)

            except Exception as e:
                logger.error("check_shift_started", message=e.message)

                raise serializers.ValidationError(_('No such user exists.'))

            is_started_shift = {"is_started_shift": is_started_shift}

            serializer = ShiftSerializer(is_started_shift)

            return Response(serializer.data)

    raise serializers.ValidationError(_('Method not allowed'))


@api_view(['GET', 'POST', ])
def end_shift(request):

    if request.method == 'POST':

        code = request.data.get('code')
        email = request.data.get('email')
        note = request.data.get('note')

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
                    shift.end_counter_balance = "0.0"
                    shift.end_note = note
                    shift.save()

            except Exception as e:
                logger.error("check_shift_started", message=e.message)
                raise serializers.ValidationError(_('No such user exists.'))

            is_started_shift = {"is_started_shift": is_started_shift}

            serializer = ShiftSerializer(is_started_shift)

            return Response(serializer.data)

    raise serializers.ValidationError(_('Method not allowed'))
