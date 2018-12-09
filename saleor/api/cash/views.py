from django.db.models import Q
from datetime import datetime
from .pagination import PostLimitOffsetPagination
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from .serializers import (
    UserTransactionSerializer,
    UserLockAuthorizationSerializer,
    UserAuthorizationSerializer,
    TerminalListSerializerNoAuth,
    TerminalListSerializer
)
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib import auth
from ...decorators import user_trail
from ...sale.models import Terminal
from saleor.shift.models import Shift
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


@api_view(['GET', 'POST'])
def login(request):
    serializer = UserAuthorizationSerializer(data=request.data)
    if request.method == 'POST':
        if serializer.is_valid():
            password = serializer.data['password']
            username = serializer.data['email']
            try:
                terminal = serializer.data['terminal']
            except:
                terminal = 'Terminal not set'
            if '@' in username:
                kwargs = {'email': username}
            else:
                kwargs = {'name': username}
            try:
                user = get_user_model().objects.get(**kwargs)
                if user.check_password(password) and user.has_perm('sale.add_drawercash') and user.has_perm(
                        'sale.change_drawercash'):
                    record_trail(request.user.name, user, terminal)
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message': 'Permission Denied!'}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'GET':
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def lock_login(request):
    serializer = UserLockAuthorizationSerializer(data=request.data)
    if request.method == 'POST':
        if serializer.is_valid():
            code = serializer.data['code']
            try:
                terminal = serializer.data['terminal']
            except:
                terminal = 'Terminal not set'
            kwargs = {'code': code}
            try:
                user = get_user_model().objects.get(**kwargs)
                if user.is_active and user.has_perm('sales.make_sale'):
                    # record_trail(user.name,user,terminal)
                    trail = str(user.name) + ' ' + \
                            ' lock login in Terminal:'
                    user_trail(user, trail, 'view')

                    # check user has already started their shift
                    now = datetime.now()
                    date_today = now.strftime("%Y-%m-%d")
                    is_started_shift = False
                    try:
                        query = Shift.objects.filter(created_at__icontains=date_today, user=user)
                        if query.exists():
                            last = query.last()
                            if last.end_time:
                                is_started_shift = False
                                # Shift.objects.create(date=time_now, start_time=time_now, user=obj,
                                #                      start_counter_balance="0.0")
                            else:
                                is_started_shift = True
                        else:
                            is_started_shift = False
                    except Exception as e:
                        logger.error("no shift details found", message=e.message, event="check_shift_started")

                    permissions = []
                    if user.has_perm('sales.make_sale'):
                        permissions.append('make_sale')
                    if user.has_perm('sales.make_invoice'):
                        permissions.append('make_invoice')
                    if user.has_perm('sales.set_ready'):
                        permissions.append('set_ready')
                    if user.has_perm('sales.set_collected'):
                        permissions.append('set_collected')

                    # check and add the custom permissions
                    try:
                        client_url_content_type = ContentType.objects.get(app_label='sales', model='unused')
                        perms = Permission.objects.filter(content_type=client_url_content_type)

                        if perms.exists():
                            for i in perms:
                                perm = (i.codename).encode('ascii', 'ignore')
                                if user.has_perm("sales." + perm):
                                    permissions.append(perm)
                    except Exception as e:
                        logger.error('error getting permissions', exception=e)

                    user_response = {"user":
                        {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "code": user.code,
                            "is_new_code": user.is_new_code,
                            "is_started_shift": is_started_shift,
                            "position": user.job_title,
                            "permissions": permissions
                        }
                    }
                    return Response(user_response, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message': 'Permission Denied!'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'GET':
        return Response(status=status.HTTP_400_BAD_REQUEST)


def record_trail(loggedin, user, terminal):
    trail = str(user.name) + ' ' + \
            str(user.email) + ' logged in Terminal:' + \
            str(terminal) + '. Session active ' + str(loggedin)
    user_trail(user, trail, 'view')


@api_view(['GET', 'POST'])
def logout(request):
    auth.logout(request)
    return Response({
        'users': "User logged out successfully"})


@api_view(['GET', 'POST'])
def terminals(request):
    query_list = Terminal.objects.all().order_by('-id')
    print query_list
    serializer = TerminalListSerializerNoAuth(query_list)
    return Response(serializer.data)


class UserAuthorizationAPIView(generics.CreateAPIView):
    """docstring for UserAuthorizationAPIView"""
    serializer_class = UserAuthorizationSerializer


class UserTransactionAPIView(generics.CreateAPIView, ):
    serializer_class = UserTransactionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        user_trail(self.request.user, 'Drawer Cash:#' + str(serializer.data['amount']) + ' added ', 'add')
        logger.info('User: ' + str(self.request.user) + ' Drawer Cash:' + str(serializer.data['amount']))


class TerminalListAPIView(generics.ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = TerminalListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Terminal.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(terminal_name__icontains=query) |
                Q(terminal_number__icontains=query)
            ).order_by('-id')
        return queryset_list
