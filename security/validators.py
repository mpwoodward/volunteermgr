import re

from django.core.exceptions import ValidationError


class PasswordComplexityValidator:
    def __init__(self):
        self.password_regex = r'(?=^.{12,}$)(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*\(\)])(?=^.*[^\s].*$).*$'

    def validate(self, password, user=None):
        if not re.match(self.password_regex, password):
            raise ValidationError(
                'The password does not meet the complexity requirements.',
                code='password_weak',
            )

    def get_help_text(self):
        return "<p>Your password must not contain spaces, and must contain at least one of each of the following:</p>" \
               "<ul>" \
               "<li>Uppercase letter</li>" \
               "<li>Lowercase letter</li>" \
               "<li>Number</li>" \
               "<li>Special character: !@#$%^&*()</li>" \
               "</ul>"
