from ckeditor.widgets import CKEditorWidget
from localflavor.us.forms import USStateField, USZipCodeField
from localflavor.us.us_states import STATE_CHOICES

from django import forms

from gis.models import ZipCode
from organization.models import Organization

from .models import Volunteer, Note, VolunteerActivity


class VolunteerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        initial = kwargs.pop('initial', None)
        user = kwargs.pop('user', None)

        kwargs['instance'] = instance
        kwargs['initial'] = initial

        super(VolunteerForm, self).__init__(*args, **kwargs)

        organizations = None
        if user.is_superuser:
            organizations = Organization.objects.all()
        elif user.organizations:
            organizations = user.organizations.all()

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

        self.fields['last_name'] = forms.CharField(required=True)
        self.fields['organization'] = forms.ModelChoiceField(queryset=organizations)
        self.fields['state'] = USStateField(required=True, widget=forms.Select(choices=states), label='State')

    class Meta:
        model = Volunteer
        fields = ['organization', 'first_name', 'preferred_name', 'middle_name', 'last_name', 'suffix',
                  'email', 'phone', 'address_1', 'address_2', 'city', 'state', 'zip', 'categories', 'sources',
                  'dt_signed_petition', 'date_signed_up', 'date_added_to_list', 'date_contacted', 'contacted_by',
                  'categories', 'details', 'is_active', ]
        widgets = {
            'details': CKEditorWidget(),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['volunteer', 'created_by', 'dt_created', 'updated_by', 'dt_updated', ]
        widgets = {
            'note': CKEditorWidget(),
        }


class VolunteerActivityForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['volunteer_activities', 'volunteer_other', 'previous_organizing_experience',
                  'active_in_presidential_primary', 'other_skills', 'facebook_profile', 'twitter_profile',
                  'instagram_profile', 'volunteer_comments', ]
        widgets = {
            'volunteer_other': CKEditorWidget(),
            'previous_organizing_experience': CKEditorWidget(),
            'active_in_presidential_primary': CKEditorWidget(),
            'other_skills': CKEditorWidget(),
            'comments': CKEditorWidget(),
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

    signed_petition = forms.BooleanField(required=False, label='Signed Petition')
    has_phone_number = forms.BooleanField(required=False, label='Has Phone Number')
    volunteer_activity = forms.ModelMultipleChoiceField(
        required=False,
        label='Volunteer Activities',
        queryset=VolunteerActivity.objects.all()
    )
    city = forms.CharField(required=False, label='City')
    zip = USZipCodeField(required=False, label='Zip')
    zip_radius = forms.IntegerField(required=False, label='Radius in Miles',
                                    help_text='Leave blank for exact zip code match')

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()

        # make sure they selected at least one search field
        if not cleaned_data.get('signed_petition') and not cleaned_data.get('volunteer_activity') \
                and not cleaned_data.get('has_phone_number') and not cleaned_data.get('city') \
                and not cleaned_data.get('state') and not cleaned_data.get('zip'):
            self.add_error('volunteer_activity', 'Please select at least one search criteria.')
        elif cleaned_data.get('zip'):
            try:
                ZipCode.objects.get(zip=cleaned_data.get('zip'))
            except ZipCode.DoesNotExist:
                self.add_error('zip', 'Invalid zip code')
        elif cleaned_data.get('zip_radius') and not cleaned_data.get('zip'):
            self.add_error('zip', 'A zip code is required when searching on zip code radius')
