from ajax_select import register, LookupChannel

from django.db.models import Q

from security.models import User


@register('staff')
class StaffLookup(LookupChannel):
    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(
            Q(last_name__istartswith=q) | Q(first_name__istartswith=q)
        ).order_by('last_name')
