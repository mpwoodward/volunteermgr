from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from ckeditor.widgets import CKEditorWidget

from dateutil.parser import parse as dateparse

from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    start_date = forms.DateField(required=True)
    start_time = forms.CharField(required=True, help_text='(e.g. 01:30 PM)')
    end_date = forms.DateField(required=False)
    end_time = forms.CharField(required=False, help_text='(e.g. 01:30 PM)')
    contact = AutoCompleteSelectField('contact', required=False, show_help_text=False)
    attendees = AutoCompleteSelectMultipleField('contact', required=False, show_help_text=False)

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        if self.instance.dt_start:
            self.fields['start_date'].initial = self.instance.dt_start.strftime('%m/%d/%Y')
            self.fields['start_time'].initial = self.instance.dt_start.strftime('%I:%M %p')

        if self.instance.dt_end:
            self.fields['end_date'].initial = self.instance.dt_end.strftime('%m/%d/%Y')
            self.fields['end_time'].initial = self.instance.dt_end.strftime('%I:%M %p')

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        try:
            dt_start = dateparse('{} {}'.format(
                cleaned_data.get('start_date').strftime('%Y-%m-%d'),
                cleaned_data.get('start_time')
            ))

            self.instance.dt_start = dt_start
        except ValueError:
            self.add_error('start_date', 'The start date or time is invalid')

        if cleaned_data.get('end_date') and not cleaned_data.get('end_time'):
            self.add_error('end_time', 'If including an end date, the end time is required')
        elif cleaned_data.get('end_date') and cleaned_data.get('end_time'):
            try:
                dt_end = dateparse('{} {}'.format(
                    cleaned_data.get('end_date').strftime('%Y-%m-%d'),
                    cleaned_data.get('end_time')
                ))

                self.instance.dt_end = dt_end
            except ValueError:
                self.add_error('end_date', 'The end date or time is invalid')

        return cleaned_data

    class Meta:
        model = Event
        fields = ['organization', 'name', 'location', 'address_1', 'address_2', 'city', 'state', 'zip',
                  'contact', 'attendees', 'url', 'details', ]
        widgets = {
            'details': CKEditorWidget(),
        }
