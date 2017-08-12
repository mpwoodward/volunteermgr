from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from gis.models import ZipCode
from gis.zip_code_functions import zips_in_radius
from phonecall.models import PhoneCall

from .forms import VolunteerForm, NoteForm, SearchForm, VolunteerActivityForm
from .models import Volunteer, Note


def search(request):
    form = SearchForm(request.GET or None, user=request.user)
    return render(request, 'volunteer/search.html', {'form': form})


def volunteer_activities(request):
    return render(request, 'volunteer/volunteer_activities.html')


def detail(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    ct = ContentType.objects.get_for_model(volunteer)
    phone_call_count = PhoneCall.objects.filter(content_type=ct, object_id=volunteer.id).count()

    return render(request, 'volunteer/detail.html', {
        'volunteer': volunteer,
        'phone_call_count': phone_call_count,
    })


def edit(request, volunteer_id=None):
    if volunteer_id:
        try:
            volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
        except Volunteer.DoesNotExist:
            raise Http404
    else:
        volunteer = None

    form = VolunteerForm(request.POST or None, instance=volunteer, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            v = form.save(commit=False)
            v.save()
            form.save_m2m()

            messages.success(request, 'The volunteer was saved.')
            return redirect('volunteer:detail', v.id)
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'volunteer/volunteer_form.html', {'form': form})


def note_edit(request, volunteer_id, note_id=None):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    if note_id:
        note = get_object_or_404(Note, id=note_id)

        # make sure this note goes with this volunteer, just in case someone is messing with the URL
        if note.volunteer_id != volunteer.id:
            raise Http404
    else:
        note = None

    form = NoteForm(request.POST or None, instance=note)

    if request.method == 'POST':
        if form.is_valid():
            n = form.save(commit=False)
            n.volunteer_id = volunteer_id

            if not n.created_by_id:
                n.created_by_id = request.user.id

            n.updated_by_id = request.user.id

            n.save()

            messages.success(request, 'The note was saved.')
            return redirect('volunteer:detail', volunteer_id)
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'volunteer/note_form.html', {'form': form})


def volunteer_activity_form(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    form = VolunteerActivityForm(request.POST or None, instance=volunteer)

    if request.method == 'POST':
        if form.is_valid():
            v = form.save(commit=False)
            v.wants_to_volunteer = True
            v.save()
            form.save_m2m()

            messages.success(request, 'The volunteer details were saved.')
            return redirect('volunteer:detail', volunteer.id)
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'volunteer/volunteer_activity_form.html', {'volunteer': volunteer, 'form': form})


def detail_tab(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    return render(request, 'volunteer/details_tab.html', {'volunteer': volunteer})


def detail_modal(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    return render(request, 'volunteer/detail_modal.html', {'volunteer': volunteer})


def volunteer_activity_tab(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    return render(request, 'volunteer/volunteer_activity_tab.html', {'volunteer': volunteer})


def phone_calls_tab(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    ct = ContentType.objects.get_for_model(volunteer)
    phone_calls = PhoneCall.objects.filter(content_type=ct, object_id=volunteer.id)

    return render(request, 'volunteer/phone_calls_tab.html', {'phone_calls': phone_calls})


def notes_tab(request, volunteer_id):
    try:
        volunteer = Volunteer.objects.get_volunteer_if_allowed(volunteer_id, request.user)
    except Volunteer.DoesNotExist:
        raise Http404

    notes = Note.objects.filter(volunteer=volunteer)

    return render(request, 'volunteer/notes_tab.html', {'notes': notes, 'volunteer_id': volunteer.id})


class VolunteersSearchJson(BaseDatatableView):
    model = Volunteer

    columns = ['last_name', 'first_name', 'email', 'phone', 'city', 'state', 'zip', 'dt_signed_petition', ]
    order_columns = ['last_name', 'first_name', '', '', 'city', 'state', 'zip', 'dt_signed_petition', ]

    max_display_length = 100

    def get_initial_queryset(self):
        volunteers = Volunteer.objects.get_volunteers_for_user(self.request.user)

        filter_kwargs = {}

        if self.request.GET.get('signed_petition'):
            filter_kwargs['dt_signed_petition__isnull'] = False

        if self.request.GET.get('volunteer_activity'):
            filter_kwargs['volunteer_activities__in'] = \
                [int(id) for id in self.request.GET.getlist('volunteer_activity')]

        if self.request.GET.get('city'):
            filter_kwargs['city__iexact'] = self.request.GET.get('city')

        if self.request.GET.get('state'):
            filter_kwargs['state'] = self.request.GET.get('state')

        if self.request.GET.get('zip') and not self.request.GET.get('zip_radius'):
            filter_kwargs['zip'] = self.request.GET.get('zip')

        volunteers = volunteers.filter(**filter_kwargs)

        if self.request.GET.get('has_phone_number'):
            volunteers = volunteers.filter(phone__isnull=False).exclude(phone='')

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
                    volunteers = volunteers.filter(zip__in=[z.zip for z in zip_codes])

        return volunteers

    def prepare_results(self, qs):
        if self.request.GET.get('signed_petition') or self.request.GET.get('has_phone_number') \
                or self.request.GET.get('volunteer_activities') or self.request.GET.get('city') \
                or self.request.GET.get('state') or self.request.GET.get('zip') \
                or self.request.GET.get('zip_radius'):
            form = SearchForm(self.request.GET or None, user=self.request.user)
            if not form.is_valid():
                return []

        data = []

        for r in qs:
            first_name = r.first_name
            if not r.is_active:
                first_name = '<strike>{}</strike>'.format(first_name)

            last_name_link = '<a href="{}">{}</a>'.format(
                reverse('volunteer:detail', args=[r.id]),
                r.last_name
            )

            if not r.is_active:
                last_name_link = '<strike>{}</strike>'.format(last_name_link)

            if r.dt_signed_petition:
                dt_signed_petition = r.dt_signed_petition.strftime('%m/%d/%Y')
            else:
                dt_signed_petition = None

            dt_created = r.dt_created.strftime('%m/%d/%Y')

            data.append(
                [
                    last_name_link,
                    first_name,
                    '<a href="mailto:{email}">{email}</a>'.format(email=r.email),
                    r.phone,
                    r.city,
                    r.state,
                    r.zip,
                    dt_signed_petition,
                    dt_created,
                ]
            )

        return data


class VolunteerActivitiesJson(BaseDatatableView):
    model = Volunteer

    columns = ['dt_created', 'last_name', 'first_name', 'email', 'volunteer_activities', 'state', 'zip', ]
    order_columns = ['dt_created', 'last_name', 'first_name', '', '', 'state', 'zip', ]

    max_display_length = 100

    def get_initial_queryset(self):
        return Volunteer.objects.get_volunteers_for_user(
            self.request.user
        ).prefetch_related(
            'volunteer_activities'
        ).order_by(
            '-dt_created',
            'last_name',
            'first_name'
        )

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            qs = qs.filter(
                Q(last_name__istartswith=search) |
                Q(first_name__istartswith=search) |
                Q(volunteer_activities__activity_short__istartswith=search) |
                Q(state__istartswith=search) |
                Q(zip__istartswith=search)
            )

        return qs

    def prepare_results(self, qs):
        data = []

        for r in qs:
            first_name = r.first_name
            if not r.is_active:
                first_name = '<strike>{}</strike>'.format(first_name)

            last_name_link = '<a href="{}">{}</a>'.format(
                reverse('volunteer:detail', args=[r.id]),
                r.last_name
            )

            volunteer_activities = ''
            if r.volunteer_activities:
                volunteer_activities = ', '.join([va.activity_short for va in r.volunteer_activities.all()])

            if not r.is_active:
                last_name_link = '<strike>{}</strike>'.format(last_name_link)

            dt_created = r.dt_created.strftime('%m/%d/%Y')

            data.append(
                [
                    dt_created,
                    last_name_link,
                    first_name,
                    '<a href="mailto:{email}">{email}</a>'.format(email=r.email),
                    volunteer_activities,
                    r.state,
                    r.zip,
                ]
            )

        return data
