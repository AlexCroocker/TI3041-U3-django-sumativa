from django import template

register = template.Library()


@register.filter
def clp(value):
    return f"${int(value):,}".replace(",", ".")
