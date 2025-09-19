from django import template
from django.core.paginator import Paginator

register = template.Library()


@register.simple_tag
def get_proper_elided_page_range(p, number, on_each_side=3, on_ends=2):
    """
    Render a proper elipted pagination that is aware of current page.

    This is needed because paginator from generic views is not aware of current page
    and so its elided method is stuck on the range of the first page.
    """
    paginator = Paginator(p.object_list, p.per_page)

    return paginator.get_elided_page_range(
        number=number,
        on_each_side=on_each_side,
        on_ends=on_ends
    )
