from dateutil.parser import parse as dateparse

from django_datatables_view.base_datatable_view import BaseDatatableView

from django.shortcuts import render

from gis.models import ZipCode
from gis.zip_code_functions import zips_in_radius
from security.decorators import require_national_lead, require_superuser

from .forms import SearchForm
from .models import PetitionSigner


@require_national_lead
def petition_signers(request):
    form = SearchForm(request.GET or None)
    return render(request, 'petition/petition_signers.html', {'form': form})


class SearchPetitionSignersJson(BaseDatatableView):
    model = PetitionSigner

    columns = ['dt_signed', 'last_name', 'first_name', 'email', 'city', 'state', 'zip', 'non_conforming_zip', ]
    order_columns = ['dt_signed', 'last_name', 'first_name', '', 'city', 'state', 'zip', '', ]

    max_display_length = 100

    def get_initial_queryset(self):
        signers = []

        if self.request.user.is_superuser:
            signers = PetitionSigner.objects.all()
        elif self.request.user.account_type.key == 'national':
            signers = PetitionSigner.objects.filter(
                state__in=[org.state for org in self.request.user.organizations.all()]
            )
        else:
            signers = PetitionSigner.objects.none()

        filter_kwargs = {}

        if self.request.GET.get('date_signed'):
            filter_kwargs['dt_signed__date'] = dateparse(self.request.GET.get('date_signed')).strftime('%Y-%m-%d')

        if self.request.GET.get('city'):
            filter_kwargs['city'] = self.request.GET.get('city')

        if self.request.GET.get('state'):
            filter_kwargs['state'] = self.request.GET.get('state')

        if self.request.GET.get('zip') and not self.request.GET.get('zip_radius'):
            filter_kwargs['zip'] = self.request.GET.get('zip')

        signers = signers.filter(**filter_kwargs)

        if self.request.GET.get('zip') and self.request.GET.get('zip_radius'):
            zip_code = None
            try:
                zip_code = ZipCode.objects.get(zip=self.request.GET.get('zip'))
            except ZipCode.DoesNotExist:
                pass

            if zip_code:
                zip_codes = zips_in_radius(
                    self.request.GET.get('zip'),
                    int(self.request.GET.get('zip_radius'))
                )

                if zip_codes:
                    signers = signers.filter(zip__in=[z.zip for z in zip_codes])

        return signers

    def prepare_results(self, qs):
        if self.request.GET.get('date_signed') or self.request.GET.get('city') \
                or self.request.GET.get('state') or self.request.GET.get('zip') \
                or self.request.GET.get('zip_radius'):
            form = SearchForm(self.request.GET or None)
            if not form.is_valid():
                return []

        data = []

        for r in qs:
            dt_signed = r.dt_signed.strftime('%m/%d/%Y')

            data.append(
                [
                    dt_signed,
                    r.last_name,
                    r.first_name,
                    '<a href="{email}">{email}</a>'.format(email=r.email),
                    r.city if r.city else '',
                    r.state if r.state else '',
                    r.zip if r.zip else '',
                    r.non_conforming_zip if r.non_conforming_zip else ''
                ]
            )

        return data
