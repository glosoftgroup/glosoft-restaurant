from rest_framework import generics
from rest_framework import pagination
from django.contrib.auth import get_user_model
from django.db.models import Q

from saleor.room.models import Maintenance as Table
from .pagination import PostLimitOffsetPagination
from .serializers import MaintenanceListSerializer

User = get_user_model()


class MaintenanceListAPIView(generics.ListAPIView):
    serializer_class = MaintenanceListSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = Table.objects.all()

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs["pk"]:
                queryset_list = Table.objects.filter(
                    room__pk=self.kwargs["pk"]
                ).select_related()
            else:
                queryset_list = Table.objects.all().order_by("-id").select_related()
        except Exception as e:
            queryset_list = Table.objects.all().select_related()
        query = self.request.GET.get("q")
        page_size = "page_size"
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get("status"):
            if self.request.GET.get("status") == "True":
                queryset_list = queryset_list.filter(is_fixed=True)
            if self.request.GET.get("status") == "False":
                queryset_list = queryset_list.filter(is_fixed=False)
        if self.request.GET.get("date"):
            queryset_list = queryset_list.filter(
                created__icontains=self.request.GET.get("date")
            )
        if query:
            queryset_list = queryset_list.filter(
                Q(room__name__icontains=query) | Q(issue__icontains=query)
            ).distinct()
        return queryset_list.order_by("-id")


class RoomMaintenanceListAPIView(generics.ListAPIView):
    serializer_class = MaintenanceListSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = Table.objects.all()

    def get_queryset(self, *args, **kwargs):
        try:
            if self.kwargs["pk"]:
                queryset_list = Table.objects.filter(
                    room__pk=self.kwargs["pk"]
                ).select_related()
            else:
                queryset_list = Table.objects.all().order_by("-id").select_related()
        except Exception as e:
            queryset_list = Table.objects.all().select_related()
        query = self.request.GET.get("q")
        page_size = "page_size"
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get("status"):
            if self.request.GET.get("status") == "True":
                queryset_list = queryset_list.filter(is_fixed=True)
            if self.request.GET.get("status") == "False":
                queryset_list = queryset_list.filter(is_fixed=False)
        if self.request.GET.get("date"):
            queryset_list = queryset_list.filter(
                created__icontains=self.request.GET.get("date")
            )
        if query:
            queryset_list = queryset_list.filter(
                Q(room__name__icontains=query) | Q(issue__icontains=query)
            ).distinct()
        return queryset_list.order_by("-id")
