from django.db.models import Q
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import pagination
from .pagination import PostLimitOffsetPagination
from .serializers import ListSaleSerializer
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


class ListAPIView(generics.ListAPIView):

    serializer_class = ListSaleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_serializer_context(self):
        if self.request.GET.get('date'):
            return {"date": self.request.GET.get('date'), 'request': self.request}
        return {"date": None, 'request': self.request}

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs['pk']:
                queryset_list = User.objects.filter(pk=self.kwargs['pk'])
            else:
                queryset_list = User.objects.all()
        except Exception as e:
            queryset_list = User.objects.all()

        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10

        if self.request.GET.get('user'):
            queryset_list = queryset_list.filter(name__icontains=int(self.request.GET.get('user')))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query) |
                Q(fullname__icontains=query) |
                Q(email__icontains=query) |
                Q(job_title__icontains=query) |
                Q(nid_icontains=query) |
                Q(nid__icontains=query)
            )
        queryset_list = queryset_list.exclude(name__iexact='glosoftg')
        return queryset_list.order_by('-id')


class ListWaitersAPIView(generics.ListAPIView):

    serializer_class = ListSaleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PostLimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = User.objects.all()

        # pagination set as 100 for the client combobox display during the daily analysis query
        # reason: to avoid pagination offset on the client combobox
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 100

        if self.request.GET.get('user'):
            queryset_list = queryset_list.filter(name__icontains=int(self.request.GET.get('user')))

        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query) |
                Q(fullname__icontains=query) |
                Q(email__icontains=query) |
                Q(job_title__icontains=query) |
                Q(nid_icontains=query) |
                Q(nid__icontains=query)
            )
        queryset_list = queryset_list.exclude(name__iexact='glosoftg')
        return queryset_list.order_by('-id')

