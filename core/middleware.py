from stronghold.middleware import LoginRequiredMiddleware

from django.utils.deprecation import MiddlewareMixin


class StrongholdLoginRequiredMiddleware(MiddlewareMixin, LoginRequiredMiddleware):
    pass
