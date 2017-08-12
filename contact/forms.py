from ckeditor.widgets import CKEditorWidget
from localflavor.us.forms import USStateField, USZipCodeField
from localflavor.us.us_states import STATE_CHOICES

from django import forms

from gis.models import ZipCode

from .models import Category, Contact, Note, Organization


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        initial = kwargs.pop('initial', None)
        user = kwargs.pop('user', None)

        kwargs['instance'] = instance
        kwargs['initial'] = initial

        super(ContactForm, self).__init__(*args, **kwargs)

        if user.is_superuser:
            states = list(STATE_CHOICES)
        else:
            user_states = [org.state for org in user.organizations.all()]
            states = []

            for state in list(STATE_CHOICES):
                if state[0] in user_states:
                    states.append(state)

        if len(states) > 1:
            states.insert(0, ('', 'Select ...'))

        self.fields['state'] = USStateField(required=True, widget=forms.Select(choices=states), label='State')

    class Meta:
        model = Contact
        fields = ['organization', 'first_name', 'preferred_name', 'middle_name', 'last_name', 'suffix',
                  'email', 'phone', 'address_1', 'address_2', 'city', 'state', 'zip', 'categories',
                  'details', 'is_active', ]
        widgets = {
            'details': CKEditorWidget(),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['contact', 'created_by', 'dt_created', 'updated_by', 'dt_updated', ]
        widgets = {
            'note': CKEditorWidget(),
        }


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        super(SearchForm, self).__init__(*args, **kwargs)

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

    organizations = forms.ModelMultipleChoiceField(
        required=False,
        label='Organizations',
        queryset=Organization.objects.all()
    )
    categories = forms.ModelMultipleChoiceField(
        required=False,
        label='Categories',
        queryset=Category.objects.all()
    )
    zip = USZipCodeField(required=False, label='Zip')
    zip_radius = forms.IntegerField(required=False, label='Radius in Miles',
                                    help_text='Leave blank for exact zip code match')

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()

        # make sure they selected at least one search field
        if not cleaned_data.get('organizations') and not cleaned_data.get('categories') \
                and not cleaned_data.get('state') and not cleaned_data.get('zip'):
            self.add_error('organizations', 'Please select at least one search criteria.')
        elif cleaned_data.get('zip'):
            try:
                ZipCode.objects.get(zip=cleaned_data.get('zip'))
            except ZipCode.DoesNotExist:
                self.add_error('zip', 'Invalid zip code')
        elif cleaned_data.get('zip_radius') and not cleaned_data.get('zip'):
            self.add_error('zip', 'A zip code is required when searching on zip code radius')
