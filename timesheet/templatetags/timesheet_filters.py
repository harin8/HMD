from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def private(obj, attr):
    """Get private attribute from object"""
    try:
        return str(getattr(obj, attr))
    except:
        return str(obj.get(attr, '')) 