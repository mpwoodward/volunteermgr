from localflavor.us.forms import USStateField, USZipCodeField
from localflavor.us.us_states import STATE_CHOICES

from django import forms


class CallSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super(CallSearchForm, self).__init__(*args, **kwargs)

        if user.is_superuser:
            states = list(STATE_CHOICES)
        else:
            user_states = [org.state for org in user.organizations.all()]
            states = []

            for state in list(STATE_CHOICES):
                if state[0] in user_states:
                    states.append(state)

        states.insert(0, ('', 'Select ...'))

        self.fields['state'] = USStateField(required=False, widget=forms.Select(choices=states), label='State')

    call_date = forms.DateField(required=False, label='Call Date')
    city = forms.CharField(required=False, label='City')
    zip = USZipCodeField(required=False, label='Zip')
    handraises = forms.BooleanField(required=False, label='Has Hand Raises')

    def clean(self):
        cleaned_data = super(CallSearchForm, self).clean()

        # make sure they selected at least one search field
        if not cleaned_data.get('call_date') and not cleaned_data.get('city') and not cleaned_data.get('state') \
                and not cleaned_data.get('zip') and not cleaned_data.get('handraises'):
            self.add_error('call_date', 'Please select at least one search criteria.')
