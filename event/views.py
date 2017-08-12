from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import EventForm
from .models import Event


def list(request):
    return render(request, 'event/list.html')


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event/event_detail.html', {'event': event})


def event_detail_tab(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event/event_detail_tab.html', {'event': event})


def event_attendees_tab(request, event_id):
    event = Event.objects.filter(pk=event_id).prefetch_related('attendees')

    if event:
        event = event[0]

    return render(request, 'event/event_attendees_tab.html', {'event': event})


def edit_event(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = None

    if request.method == 'GET':
        if event:
            form = EventForm(instance=event)
        else:
            form = EventForm()
    elif request.method == 'POST':
        if event:
            form = EventForm(request.POST, instance=event)
        else:
            form = EventForm(request.POST)

        if form.is_valid():
            event = form.save()
            messages.success(request, 'The event was saved.')
            return redirect('event:event_detail', event.id)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'event/event_form.html', {'form': form})


class EventsJson(BaseDatatableView):
    model = Event

    columns = ['name', 'dt_start', 'dt_end', 'location', 'url', 'contact', ]
    order_columns = ['name', 'dt_start', '', '', '', 'contact', ]

    max_display_length = 100

    def prepare_results(self, qs):
        data = []

        for r in qs:
            name_link = '<a href="{}">{}</a>'.format(
                reverse('event:event_detail', args=[r.id]),
                r.name
            )

            url_link = None
            if r.url:
                url_link = '<a href="{}" target="_blank"><span class="glyphicon glyphicon-new-window"></span></a>'.format(r.url)

            dt_start = r.dt_start.strftime('%Y-%m-%d @ %I:%M %p')

            dt_end = None
            if r.dt_end:
                dt_end = r.dt_end.strftime('%Y-%m-%d @ %I:%M %p')

            contact_link = None
            if r.contact:
                contact_link = '<a data-toggle="modal" href="{}" data-target="#contactDetailModal" data-remote="false">{}</a>'.format(
                    reverse('contact:detail_modal', args=[r.contact.id]),
                    r.contact.short_name
                )

            data.append(
                [
                    name_link,
                    dt_start,
                    dt_end,
                    r.location,
                    url_link,
                    contact_link,
                ]
            )

        return data
