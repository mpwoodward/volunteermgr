from ckeditor.widgets import CKEditorWidget
from localflavor.us.forms import USStateField, USZipCodeField

from django import forms

from security.models import AccountType, User

from .models import Organization

from localflavor.us.us_states import STATE_CHOICES


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ['dt_created', 'dt_updated', ]
        widgets = {
            'comments': CKEditorWidget(),
        }


class StaffForm(forms.ModelForm):
    zip = USZipCodeField(required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        initial = kwargs.pop('initial', {})
        self.user = kwargs.pop('user')

        kwargs['instance'] = instance
        kwargs['initial'] = initial

        super(StaffForm, self).__init__(*args, **kwargs)

        account_types = None
        if self.user.is_superuser:
            account_types = AccountType.objects.all()
        else:
            account_types = AccountType.objects.filter(
                permission_hierarchy__gt=self.user.account_type.permission_hierarchy
            )

        organizations = None
        if self.user.is_superuser:
            organizations = Organization.objects.all()
        else:
            organizations = self.user.organizations.all()

        if self.user.is_superuser:
            states = list(STATE_CHOICES)
        else:
            user_states = [org.state for org in self.user.organizations.all()]
            states = []

            for state in list(STATE_CHOICES):
                if state[0] in user_states:
                    states.append(state)

        if len(states) > 1:
            states.insert(0, ('', 'Select ...'))

        self.fields['state'] = USStateField(required=True, widget=forms.Select(choices=states), label='State')
        self.fields['account_type'] = forms.ModelChoiceField(queryset=account_types)
        self.fields['organizations'] = forms.ModelMultipleChoiceField(queryset=organizations)

    def clean(self):
        cleaned_data = super(StaffForm, self).clean()

        if not cleaned_data.get('is_superuser') and not cleaned_data.get('account_type'):
            self.add_error('account_type', 'Account type is required')

        if not self.user.is_superuser:
            cleaned_data['is_superuser'] = False

    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'created_by', 'dt_created', 'updated_by', 'dt_updated', 'dt_last_login', ]
