from ckeditor.fields import RichTextField
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField

from django.db import models


class Organization(models.Model):
    key = models.CharField(max_length=50, blank=True, null=True, verbose_name='Key')
    name = models.CharField(max_length=250, unique=True, verbose_name='Name')
    state = USStateField(blank=True, null=True, verbose_name='State')
    zip = USZipCodeField(blank=True, null=True, verbose_name='Zip')
    phone = PhoneNumberField(blank=True, null=True, verbose_name='Phone')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    url = models.URLField(blank=True, null=True, verbose_name='URL')
    comments = RichTextField(blank=True, null=True, verbose_name='Comments')
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name', ]
