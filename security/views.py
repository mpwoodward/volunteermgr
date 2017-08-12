from datetime import datetime

import requests

from stronghold.decorators import public

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters

from .forms import ChangePasswordForm, LoginForm, ResetPasswordForm
from .models import User


@public
@sensitive_post_parameters('password')
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password')
            )

            # users must be active and (have an account type and be in at least one organization) or be a superuser
            if user and user.is_active:
                if user.is_superuser or (user.account_type and user.organizations):
                    login(request, user)

                    user.dt_last_login = datetime.now()
                    user.save()

                    if user.password_reset:
                        messages.info(request, 'Please set a new password.')
                        return redirect('security:change_password')
                    elif request.GET.get('next', False):
                        return redirect(request.GET.get('next'))
                    else:
                        return redirect(settings.LOGIN_REDIRECT_URL)
                else:
                    messages.error(request, 'Your login failed. Please try again.')
                    return redirect(settings.LOGIN_URL)
            else:
                messages.error(request, 'Your login failed. Please try again.')
                return redirect(settings.LOGIN_URL)
        else:
            messages.error(request, 'Please provide both an email and password.')
            return redirect(settings.LOGIN_URL)
    elif request.method == 'GET':
        if not request.user.is_authenticated():
            return render(request, 'security/login.html', {'form': LoginForm()})
        else:
            return redirect(settings.LOGIN_REDIRECT_URL)


def user_logout(request):
    logout(request)
    messages.success(request, "You're logged out.")

    return redirect(settings.LOGIN_URL)


def change_password(request):
    form = ChangePasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            try:
                validate_password(form.cleaned_data.get('password'), user=request.user)
                request.user.set_password(form.cleaned_data.get('password'))
                request.user.password_reset = False
                request.user.save()

                logout(request)

                messages.success(request, 'Your password was changed. Please login using your new password.')
                return redirect(settings.LOGIN_URL)
            except ValidationError as e:
                error_message = '<ul>'
                for message in e.messages:
                    error_message += '<li>{}</li>'.format(message)
                error_message += '</ul>'

                messages.error(
                    request,
                    'Your password does not meet the password requirements: {}'.format(error_message)
                )
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'security/change_password_form.html',
                  {'form': form, 'password_validators_help_texts': password_validators_help_texts()})


@public
def reset_password(request):
    form = ResetPasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            recaptacha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptacha_response
            }
            r = requests.post(settings.RECAPTCHA_VERIFY_URL, data=data)
            result = r.json()

            if result['success']:
                try:
                    user = User.objects.get(
                        email__iexact=form.cleaned_data.get('email'),
                        is_active=True
                    )
                    new_password = User.objects.make_random_password()
                    user.set_password(new_password)
                    user.password_reset = True
                    user.save()

                    send_mail(
                        '{} Password Reset'.format(settings.SITE_NAME),
                        'Your temporary password is: {}\n\nPlease visit {} and login with this password. You '
                        'will then be asked to reset your password.'.format(new_password, settings.SITE_URL),
                        settings.FROM_EMAIL,
                        [user.email, ],
                        fail_silently=False
                    )

                    messages.success(request, 'A new temporary password has been emailed to you.')
                    return redirect(settings.LOGIN_URL)
                except User.DoesNotExist:
                    messages.error(request, 'No account with that email address exists. Please verify your email address.')
            else:
                messages.error(request, 'Invalid reCAPTCHA response. Please try again.')
        else:
            messages.error(request, 'Please correct the errors highlighted below.')

    return render(request, 'security/forgot_password.html',
                  {'form': form, 'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY})
