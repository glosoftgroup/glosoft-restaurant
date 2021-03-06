from datetime import datetime, time
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView
from saleor.utils import is_shift_started

from structlog import get_logger

logger = get_logger(__name__)

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class CustomJWTSerializer(JSONWebTokenSerializer):
    def validate(self, attrs):
        # email comes as the code
        username = attrs.get('email')
        password = attrs.get('password')

        # check the working period first
        time_now = datetime.now().time()

        if username and password:
            username = username.lower()
            if '@' in username:
                kwargs = {'email': username}
            else:
                kwargs = {'code': username}

            try:
                us = get_user_model().objects.get(**kwargs)
            except ObjectDoesNotExist as ex:
                logger.error("could not get user details", exception=ex)
                msg = _('Invalid User Credentials.')
                raise serializers.ValidationError(msg)

            user = authenticate(username=us.email, password=us.rest_code)

            if user:
                logger.info('successful authentication', user=user)
                if not user.is_active:
                    logger.info('unauthorized user login, user not active', user=user)
                    msg = _('Unauthorized User Login.')
                    raise serializers.ValidationError(msg)

                if not user.has_perm('sales.code_login'):
                    logger.info('unauthorized user login, user has no permissions', user=user)
                    msg = _('Unauthorized User Login.')
                    raise serializers.ValidationError(msg)

                if not is_shift_started():
                    """ check permission for changing main shift """
                    if not user.has_perm('sales.change_shift'):
                        logger.info('close main shift, user has no permissions to start shift', user=user)
                        msg = _('MAIN SHIFT IS CLOSED.')
                        raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user,
                    'permissions': user.get_all_permissions(),
                    'main_shift_status': is_shift_started()
                }
            else:
                logger.info('invalid user credentials, user not authenticated')
                msg = _('Invalid User Credentials.')
                raise serializers.ValidationError(msg)
        else:
            logger.info('error authorizing empty code')
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class ObtainJSONWebToken(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    # serializer_class = JSONWebTokenSerializer
    serializer_class = CustomJWTSerializer
