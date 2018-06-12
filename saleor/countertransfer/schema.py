import graphene

from graphene_django.types import DjangoObjectType

from .models import CounterTransfer as Transfer
from .models import CounterTransferItems as Items


class TransferType(DjangoObjectType):
    class Meta:
        model = Transfer


class ItemsType(DjangoObjectType):
    class Meta:
        model = Items


class Query(object):
    counter_transfer = graphene.Field(TransferType,
                              id=graphene.Int(),
                              name=graphene.String())
    all_counter_transfer = graphene.List(TransferType)

    transfer_items = graphene.Field(ItemsType,
                                id=graphene.Int(),
                                name=graphene.String())
    all_transfer_items = graphene.List(ItemsType)

    def resolve_all_counter_transfer(self, info, **kwargs):
        return Transfer.objects.all()

    def resolve_all_transfer_items(self, info, **kwargs):
        return Items.objects.all()

    def resolve_counter_transfer(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')

        if id is not None:
            return Transfer.objects.get(pk=id)

        if name is not None:
            return Transfer.objects.get(name=name)

        return None

    def resolve_transfer_items(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')

        if id is not None:
            return Items.objects.get(pk=id)

        if name is not None:
            return Items.objects.get(name=name)

        return None