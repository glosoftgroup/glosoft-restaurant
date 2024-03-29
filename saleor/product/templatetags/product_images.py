import re
import warnings

from django import template
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from structlog import get_logger

logger = get_logger(__name__)

register = template.Library()


# cache available sizes at module level
def get_available_sizes():
    all_sizes = set()
    keys = settings.VERSATILEIMAGEFIELD_RENDITION_KEY_SETS
    for size_group, sizes in keys.items():
        for size_name, size in sizes:
            all_sizes.add(size)
    return all_sizes


AVAILABLE_SIZES = get_available_sizes()


def choose_placeholder(size=''):
    # type: (str) -> str
    """Assign placeholder at least as big as provided size if possible.
    When size is bigger than available, return the biggest.
    If size is invalid or not provided, return DEFAULT_PLACEHOLDER"""
    placeholder = settings.DEFAULT_PLACEHOLDER
    parsed_sizes = re.match(r'(\d+)x(\d+)', size)
    available_sizes = sorted(settings.PLACEHOLDER_IMAGES.keys())
    if parsed_sizes and available_sizes:
        # check for placeholder equal or bigger than requested picture
        x_size, y_size = parsed_sizes.groups()
        max_size = max([int(x_size), int(y_size)])
        bigger_or_eq = list(filter(lambda x: x >= max_size, available_sizes))
        if len(bigger_or_eq) > 0:
            placeholder = settings.PLACEHOLDER_IMAGES[bigger_or_eq[0]]
        else:
            placeholder = settings.PLACEHOLDER_IMAGES[available_sizes[-1]]
    return placeholder


@register.simple_tag()
def get_thumbnail(instance, size, method='crop'):
    size_name = '%s__%s' % (method, size)
    if instance:
        if (size_name not in AVAILABLE_SIZES and not
                settings.VERSATILEIMAGEFIELD_SETTINGS['create_images_on_demand']):
            msg = ('Thumbnail size %s is not defined in settings '
                   'and it won\'t be generated automatically' % size_name)
            warnings.warn(msg)
        try:
            if method == 'crop':
                thumbnail = instance.crop[size]
            else:
                thumbnail = instance.thumbnail[size]
        except:
            logger.exception('Thumbnail fetch failed',
                             extra={'instance': instance, 'size': size})
        else:
            return thumbnail.url
    return static(choose_placeholder(size))


@register.simple_tag()
def product_first_image(product, size, method='crop'):
    """
    Returns main product image
    """
    all_images = product.images.all()
    main_image = all_images[0].image if all_images else None
    return get_thumbnail(main_image, size, method)
