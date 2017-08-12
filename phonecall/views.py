from dateutil.parser import parse as dateparse

from django_datatables_view.base_datatable_view import BaseDatatableView

from django.db.models import Q
from django.shortcuts import render

from .forms import CallSearchForm
from .models import PhoneCall


def calls(request):
    form = CallSearchForm(request.GET or None, user=request.user)
    return render(request, 'phonecall/calls.html', {'form': form})


class SearchCallsJson(BaseDatatableView):
    model = PhoneCall

    columns = ['call_date', 'last_name', 'first_name', 'email', 'city', 'state', 'zip', 'handraises', 'content_type', ]
    order_columns = ['call_date', 'last_name', 'first_name', '', 'city', 'state', 'zip', '', 'content_type', ]

    max_display_length = 100

    def get_initial_queryset(self):
        calls = PhoneCall.objects.get_phone_calls_for_user(self.request.user).prefetch_related('content_object')

        filter_kwargs = {}

        if self.request.GET.get('call_date'):
            filter_kwargs['call_date'] = dateparse(self.request.GET.get('call_date')).strftime('%Y-%m-%d')

        if self.request.GET.get('city'):
            filter_kwargs['city'] = self.request.GET.get('city')

        if self.request.GET.get('state'):
            filter_kwargs['state'] = self.request.GET.get('state')

        if self.request.GET.get('zip'):
            filter_kwargs['zip'] = self.request.GET.get('zip')

        if self.request.GET.get('handraises'):
            filter_kwargs['handraises__isnull'] = False

        return calls.filter(**filter_kwargs)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            qs = qs.filter(
                Q(volunteer_phonecalls__last_name__istartswith=search) |
                Q(volunteer_phonecalls__first_name__istartswith=search) |
                Q(user_phonecalls__first_name__istartswith=search) |
                Q(user_phonecalls__last_name__istartswith=search) |
                Q(first_name__istartswith=search) |
                Q(last_name__istartswith=search) |
                Q(city__istartswith=search) |
                Q(state__istartswith=search) |
                Q(zip__istartswith=search)
            )

        return qs

    def prepare_results(self, qs):
        data = []

        for r in qs:
            call_date = r.call_date.strftime('%m/%d/%Y')

            handraises = ''
            if r.handraises:
                handraises = ', '.join(r.handraises)

            user_type = ''
            if r.content_type:
                user_type = r.content_type.model.title()
                if user_type == 'User':
                    user_type = 'Staff'
            else:
                user_type = 'Caller'

            last_name = r.last_name if r.last_name else ''
            first_name = r.first_name if r.first_name else ''

            if r.content_object:
                last_name = r.content_object.last_name
                first_name = r.content_object.first_name

            data.append(
                [
                    call_date,
                    last_name,
                    first_name,
                    '<a href="{email}">{email}</a>'.format(email=r.email) if r.email else '',
                    r.city if r.city else '',
                    r.state if r.state else '',
                    r.zip if r.zip else '',
                    handraises,
                    user_type,
                ]
            )

        return data
