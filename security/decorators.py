from django.core.exceptions import PermissionDenied


def require_superuser(f):
    def decorator(request, *args, **kwargs):
        if request.user.is_superuser:
            return f(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    return decorator


def require_national_lead(f):
    def decorator(request, *args, **kwargs):
        if not request.user.is_superuser and \
                (not request.user.account_type or request.user.account_type.key != 'national'):
            raise PermissionDenied()
        else:
            return f(request, *args, **kwargs)

    return decorator


def require_manage_staff_permissions(f):
    allowed_account_type_keys = ('national', 'state', )

    def decorator(request, *args, **kwargs):
        if not request.user.is_superuser and \
                (not request.user.account_type or request.user.account_type.key not in allowed_account_type_keys):
            raise PermissionDenied()
        else:
            return f(request, *args, **kwargs)

    return decorator
