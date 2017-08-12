from django import forms


class ChangePasswordForm(forms.Form):
    password = forms.CharField(error_messages={'required': 'Password is required'},
                               widget=forms.PasswordInput())
    password2 = forms.CharField(error_messages={'required': 'Password is required'},
                                widget=forms.PasswordInput())

    def clean(self, *args, **kwargs):
        cleaned_data = super(ChangePasswordForm, self).clean()

        if cleaned_data.get('password') != cleaned_data.get('password2'):
            self.add_error('password2', 'The passwords do not match')


class LoginForm(forms.Form):
    email = forms.EmailField(error_messages={'required': 'Email is required.'})
    password = forms.CharField(error_messages={'required': 'Password is required.'},
                               widget=forms.PasswordInput())


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(error_messages={'required': 'Email is required.'})
