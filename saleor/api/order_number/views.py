from rest_framework.response import Response
from ...orders.models import Orders
import random
from rest_framework.decorators import api_view
from .serializers import (
    OrderNumberSerializer,
     )


class Comment(object):
    def __init__(self, number, last_order_id):
        self.number = number
        self.last_order_id = last_order_id


@api_view(['GET', 'POST', ])
def new_order(request):
    try:
        number = int(Orders.objects.latest('id').id)# + random.randrange(6) + request.user.id
        last_order_id = number + 1
    except Exception as e:
        number = random.randrange(10) + request.user.id
        last_order_id = 1
    order_number = Comment(number='RET#'+str(request.user.id)+str(''.join(random.choice('0123456789ABCDEF') for i in range(3)))+'-'+str(number), last_order_id=last_order_id)
    serializer = OrderNumberSerializer(order_number)
    return Response(serializer.data)


