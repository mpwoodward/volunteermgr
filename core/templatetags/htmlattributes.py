from django import template


register = template.Library()


@register.filter()
def htmlattributes(value, arg):
    attrs = value.field.widget.attrs

    kvs = arg.split(',')

    for s in kvs:
        kv = s.split(':')
        attrs[kv[0]] = kv[1]

    rendered = str(value)

    return rendered
