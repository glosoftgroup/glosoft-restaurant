import graphene
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.shortcuts import _get_queryset
from django.db import models

# First we create a little helper function, becase we will potentially have many PaginatedTypes
# and we will potentially want to turn many querysets into paginated results:

def get_paginator(qs, page_size, page, paginated_type, **kwargs):
    p = Paginator(qs, page_size)
    # query = qs.values_list('date').annotate(total_item=models.Sum('counter_transfer_items__transferred_qty'))
    # items = list()
    # for item in query:
    #     items.append(item)
    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return paginated_type(
        page=page_obj.number,
        pages=p.num_pages,
        total=p.count,
        has_next=page_obj.has_next(),
        has_prev=page_obj.has_previous(),
        # items=items,
        results=page_obj.object_list,
    )


class CategoryAncestorsCache(object):
    """
    Cache used to store ancestors of a category in GraphQL context in order to
    reduce number of database queries. Categories of the same tree depth level
    have common ancestors, which allows us to cache them by the level.
    """

    def __init__(self, category):
        self._cache = {category.level: category.get_ancestors()}

    def get(self, category):
        if category.level not in self._cache:
            self._cache[category.level] = category.get_ancestors()
        return self._cache[category.level]


class DjangoPkInterface(graphene.Interface):
    """
    Exposes the Django model primary key
    """
    pk = graphene.ID(description="Primary key")

    def resolve_pk(self, args, context, info):
        return self.pk


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except AttributeError:
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_none() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    except queryset.model.DoesNotExist:
        return None
