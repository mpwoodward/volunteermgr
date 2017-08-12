from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from security.decorators import require_manage_staff_permissions, require_superuser
from security.models import User

from .forms import StaffForm, OrganizationForm
from .models import Organization


def list(request):
    return render(request, 'organization/list.html')


def detail(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    staff = User.objects.filter(organizations__in=[organization]).prefetch_related('teams')
    return render(request, 'organization/detail.html', {'organization': organization, 'staff': staff})


@require_superuser
def organization_form(request, organization_id=None):
    if organization_id:
        organization = get_object_or_404(Organization, pk=organization_id)
    else:
        organization = None

    form = OrganizationForm(request.POST or None, instance=organization)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'The chapter was saved.')
            return redirect('organization:list')
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'organization/organization_form.html', {'form': form})


def staff(request):
    return render(request, 'organization/staff.html')


@require_manage_staff_permissions
def staff_form(request, staff_id=None):
    if staff_id:
        try:
            staff = User.objects.get_user_if_allowed(staff_id, request.user)
        except User.DoesNotExist:
            raise PermissionDenied()
    else:
        staff = None

    form = StaffForm(request.POST or None, user=request.user, instance=staff)

    if request.method == 'POST':
        if form.is_valid():
            s = form.save(commit=False)

            if not s.id:  # new staff, set random password
                s.set_password(User.objects.make_random_password())

            if not s.created_by_id:
                s.created_by_id = request.user.id

            s.updated_by_id = request.user.id
            s.save()
            form.save_m2m()

            messages.success(request, 'The staff member was saved successfully')
            return redirect('organization:staff')
        else:
            messages.error(request, 'Please correct the errors highlighted below')

    return render(request, 'organization/staff_form.html', {'form': form})


class OrganizationsJson(BaseDatatableView):
    model = Organization

    columns = ['name', 'state', 'national_leads', 'state_leads', ]
    order_columns = ['name', 'state', '', '', ]

    max_display_length = 100

    def get_initial_queryset(self):
        return Organization.objects.all().prefetch_related('user_set')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            qs = qs.filter(
                Q(name__istartswith=search) |
                Q(state__istartswith=search) |
                Q(user__first_name__istartswith=search) |
                Q(user__last_name__istartswith=search)
            )

        return qs

    def prepare_results(self, qs):
        data = []

        for r in qs:
            name_link = '<a href="{}">{}</a>'.format(
                reverse('organization:detail', args=[r.id]),
                r.name
            )

            state_leads = ''
            national_leads = ''
            if r.user_set:
                for lead in r.user_set.all():
                    if lead.account_type:
                        if lead.account_type.type == 'National Lead':
                            national_leads += '<a href="mailto:{}">{} {}</a>, '.format(
                                lead.email,
                                lead.first_name,
                                lead.last_name,
                            )
                        elif lead.account_type.type == 'State Lead':
                            state_leads += '<a href="mailto:{}">{} {}</a>, '.format(
                                lead.email,
                                lead.first_name,
                                lead.last_name,
                            )

                if state_leads:
                    state_leads = state_leads[:-2]

                if national_leads:
                    national_leads = national_leads[:-2]

            if not r.is_active:
                name_link = '<strike>{}</strike>'.format(name_link)

            data.append(
                [
                    name_link,
                    r.state,
                    national_leads,
                    state_leads,
                ]
            )

        return data


class StaffJson(BaseDatatableView):
    model = User

    columns = ['last_name', 'first_name', 'email', 'phone', 'organizations', 'account_type.type', 'is_superuser', ]
    order_columns = ['last_name', 'first_name', '', '', '', 'account_type.type', '', 'is_superuser', ]

    max_display_length = 100

    def get_initial_queryset(self):
        return User.objects.all().prefetch_related('organizations')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            qs = qs.filter(
                Q(last_name__istartswith=search) |
                Q(first_name__istartswith=search) |
                Q(account_type__type__istartswith=search) |
                Q(organizations__name__istartswith=search)
            ).order_by(
                'last_name',
                'first_name'
            ).distinct(
                'last_name',
                'first_name'
            )

        return qs

    def prepare_results(self, qs):
        data = []

        for r in qs:
            if self.request.user.is_superuser \
                    or (r.account_type and \
                            self.request.user.account_type.permission_hierarchy < r.account_type.permission_hierarchy):
                last_name_link = '<a href="{}">{}</a>'.format(
                    reverse('organization:edit_staff', kwargs={'staff_id': r.id}),
                    r.last_name
                )
            else:
                last_name_link = r.last_name

            organizations = ''
            if r.organizations:
                organizations = ', '.join([org.name for org in r.organizations.all()])

            green_check = '<span class="glyphicon glyphicon-ok-circle" style="color:green;"></span>'
            red_x = '<span class="glyphicon glyphicon-ban-circle" style="color:red;"></span>'

            is_superuser = green_check if r.is_superuser else red_x

            data.append(
                [
                    last_name_link,
                    r.first_name,
                    '<a href="mailto:{email}">{email}</a>'.format(email=r.email) if r.email else '',
                    r.phone if r.phone else '',
                    organizations,
                    r.account_type.type if r.account_type else '',
                    is_superuser,
                ]
            )

        return data
