"""Shared template filters and tags.

Kept small and presentation-only; no business logic lives in templates or
template tags.
"""

from django import template

register = template.Library()


@register.filter
def split(value: str, separator: str = ",") -> list[str]:
    """Split a string into a list on ``separator``, trimming whitespace.

    Usage::

        {% for label in "Dashboard,Profile"|split:"," %}
    """
    if not value:
        return []
    return [part.strip() for part in str(value).split(separator)]


@register.simple_tag
def get_low_stock_alerts():
    """Retrieve products that have fallen below minimum stock thresholds."""
    from django.db.models import F

    from apps.catalog.models import Product
    return Product.objects.alive().filter(current_stock__lte=F("minimum_stock")).order_by("current_stock")[:10]

