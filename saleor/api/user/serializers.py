from rest_framework import serializers
from django.contrib.auth import get_user_model
from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()


class ListSaleSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'fullname',
            'nid',
            'mobile',
            'code',
            'date_joined',
            'is_staff',
            'is_active',
            'is_new_code',
            'send_mail'
        )
