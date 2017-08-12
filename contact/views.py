from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from gis.models import ZipCode
from gis.zip_code_functions import zips_in_radius

from .forms import ContactForm, NoteForm, SearchForm
from .models import Contact, Note


def search(request):
    form = SearchForm(request.GET or None, user=request.user)
    return render(request, 'contact/search.html', {'form': form})


def detail(request, contact_id):
    try:
        contact = Contact.objects.get_contact_if_allowed(contact_id, request.user)
    except Contact.DoesNotExist:
        raise Http404

    return render(request, 'contact/detail.html', {
        'contact': contact,
    })


def edit(request, contact_id=None):
    if contact_id:
        try:
            contact = Contact.objects.get_contact_if_allowed(contact_id, request.user)
        except Contact.DoesNotExist:
            raise Http404
    else:
        contact = None

    form = ContactForm(request.POST or None, user=request.user, instance=contact)

    if request.method == 'POST':
        if form.is_valid():
            c = form.save(commit=False)
            c.save()
            form.save_m2m()

            messages.success(request, 'The contact was saved.')
            return redirect('contact:detail', c.id)
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'contact/contact_form.html', {'form': form})


def note_edit(request, contact_id, note_id=None):
    try:
        contact = Contact.objects.get_contact_if_allowed(contact_id, request.user)
    except Contact.DoesNotExist:
        raise Http404

    if note_id:
        note = get_object_or_404(Note, id=note_id)

        # make sure this note goes with this contact, just in case someone is messing with the URL
        if note.contact_id != contact.id:
            raise Http404
    else:
        note = None

    form = NoteForm(request.POST or None, instance=note)

    if request.method == 'POST':
        if form.is_valid():
            n = form.save(commit=False)
            n.contact_id = contact_id

            if not n.created_by_id:
                n.created_by_id = request.user.id

            n.updated_by_id = request.user.id

            n.save()

            messages.success(request, 'The note was saved.')
            return redirect('contact:detail', contact_id)
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'contact/note_form.html', {'form': form})


def detail_tab(request, contact_id):
    try:
        contact = Contact.objects.get_contact_if_allowed(contact_id, request.user)
    except Contact.DoesNotExist:
        raise Http404

    return render(request, 'contact/details_tab.html', {'contact': contact})


def detail_modal(request, contact_id):
    try:
        contact = Contact.objects.get_contact_if_allowed(contact_id, request.user)
    except Contact.DoesNotExist:
        raise Http404

    return render(request, 'contact/detail_modal.html', {'contact': contact})


def notes_tab(request, contact_id):
    try:
        contact = Contact.objects.get_contact_if_allowed(contact_id, request.user)
    except Contact.DoesNotExist:
        raise Http404

    notes = Note.objects.filter(contact=contact)

    return render(request, 'contact/notes_tab.html', {'notes': notes, 'contact_id': contact.id})


class SearchJson(BaseDatatableView):
    model = Contact

    columns = ['organization', 'last_name', 'first_name', 'email', 'phone', 'state', 'zip', 'categories', ]
    order_columns = ['organization', 'last_name', 'first_name', '', '', 'state', 'zip', '', ]

    max_display_length = 100

    def get_initial_queryset(self):
        contacts = Contact.objects.get_contacts_for_user(self.request.user)

        filter_kwargs = {}

        if self.request.GET.get('organizations'):
            filter_kwargs['organization__in'] = [int(id) for id in self.request.GET.getlist('organizations')]

        if self.request.GET.get('categories'):
            filter_kwargs['categories__in'] = \
                [int(id) for id in self.request.GET.getlist('categories')]

        if self.request.GET.get('state'):
            filter_kwargs['state'] = self.request.GET.get('state')

        if self.request.GET.get('zip') and not self.request.GET.get('zip_radius'):
            filter_kwargs['zip'] = self.request.GET.get('zip')

        contacts = contacts.filter(**filter_kwargs)

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
                    contacts = contacts.filter(zip__in=[z.zip for z in zip_codes])

        return contacts

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            qs = qs.filter(
                Q(organization__name__istartswith=search) |
                Q(last_name__istartswith=search) |
                Q(first_name__istartswith=search) |
                Q(state__istartswith=search) |
                Q(zip__istartswith=search) |
                Q(categories__category__istartswith=search)
            )

        return qs

    def prepare_results(self, qs):
        if self.request.GET.get('organizations') or self.request.GET.get('categories') \
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
                reverse('contact:detail', args=[r.id]),
                r.last_name
            )

            if not r.is_active:
                last_name_link = '<strike>{}</strike>'.format(last_name_link)

            categories = ''
            if r.categories:
                categories = ', '.join([c.category for c in r.categories.all()])

            data.append(
                [
                    r.organization.name if r.organization else '',
                    last_name_link,
                    first_name,
                    '<a href="mailto:{email}">{email}</a>'.format(email=r.email),
                    r.phone if r.phone else '',
                    r.state if r.state else '',
                    r.zip if r.zip else '',
                    categories,
                ]
            )

        return data
