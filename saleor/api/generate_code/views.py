from rest_framework.response import Response
from ...userprofile.models import User
import random
from rest_framework.decorators import api_view
from .serializers import (
    CodeNumberSerializer,
     )


@api_view(['GET', 'POST', ])
def new_code(request):

    code = generate_code()

    code_number = {"code": code}

    serializer = CodeNumberSerializer(code_number)

    return Response(serializer.data)


def generate_code():

    code = str(random.randint(10000, 99999))

    try:
        """ check if code exists """
        user = User.objects.get(code=code)
        print user
        if user:
            generate_code()
    except Exception as e:
        pass

    return code


