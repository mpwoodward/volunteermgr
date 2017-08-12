from ajax_select import register, LookupChannel

from django.db.models import Q

from contact.models import Contact


@register('attendee')
class AttendeeLookup(LookupChannel):
    model = Contact

    def get_query(self, q, request):
        return self.model.objects.filter(
            Q(last_name__istartswith=q) | Q(first_name__istartswith=q)
        ).order_by('last_name')
