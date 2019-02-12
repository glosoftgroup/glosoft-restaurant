from rest_framework.response import Response
from django.utils.translation import ugettext as _
from rest_framework import serializers
from ...userprofile.models import User
import random
from rest_framework.decorators import api_view
from .serializers import (
    CodeNumberSerializer,
     )


@api_view(['GET', 'POST', ])
def new_code(request):

    """" generate the unique code """

    code = generate_code()

    if request.method == 'POST':

        post_code = request.data.get('code')
        post_email = request.data.get('email')

        if post_code and post_email:

            """ get user and set is_new_code to False """

            try:

                user = User.objects.get(code=post_code, email=post_email)
                user.is_new_code = False
                user.code = code
                user.save()

            except Exception as e:

                raise serializers.ValidationError(_('No such user exists.'))

    code_number = {"code": code}

    serializer = CodeNumberSerializer(code_number)

    return Response(serializer.data)


def generate_code():

    code = str(random.randint(10000, 99999))

    try:

        """ check if code exists """

        user = User.objects.get(code=code)

        if user:

            generate_code()

    except Exception as e:
        pass

    return code


