from localflavor.us.forms import USStateField, USZipCodeField
from localflavor.us.us_states import STATE_CHOICES

from django import forms

from gis.models import ZipCode


class SearchForm(forms.Form):
    STATES = list(STATE_CHOICES)
    STATES.insert(0, ('', 'Select ...'))

    date_signed = forms.DateField(required=False, label='Date Signed')
    city = forms.CharField(required=False, label='City')
    state = USStateField(required=False, widget=forms.Select(choices=STATES), label='State')
    zip = USZipCodeField(required=False, label='Zip')
    zip_radius = forms.IntegerField(required=False, label='Radius in Miles',
                                    help_text='Leave blank for exact zip code match')

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()

        # make sure they selected at least one search field
        if not cleaned_data.get('date_signed') and not cleaned_data.get('city') \
                and not cleaned_data.get('state') and not cleaned_data.get('zip') \
                and not cleaned_data.get('zip_radius'):
            self.add_error('date_signed', 'Please select at least one search criteria.')
        elif cleaned_data.get('zip'):
            try:
                ZipCode.objects.get(zip=cleaned_data.get('zip'))
            except ZipCode.DoesNotExist:
                self.add_error('zip', 'Invalid zip code')
        elif cleaned_data.get('zip_radius') and not cleaned_data.get('zip'):
            self.add_error('zip', 'A zip code is required when searching on zip code radius')
