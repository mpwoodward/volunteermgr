from ckeditor.fields import RichTextField
from localflavor.us.models import USStateField, USZipCodeField

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models

from security.models import User
from volunteer.models import Volunteer


class PhoneCallManager(models.Manager):
    def get_phone_calls_for_user(self, requester):
        if requester.is_superuser:
            return self.all()
        else:
            return self.filter(
                state__in=[org.state for org in requester.organizations.all()]
            )


class PhoneCall(models.Model):
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    call_date = models.DateField(verbose_name='Call Date')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    pin = models.PositiveIntegerField(verbose_name='PIN')
    caller_id = models.CharField(max_length=20, verbose_name='Caller ID')
    email = models.EmailField(verbose_name='Email')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    state = USStateField(blank=True, null=True, verbose_name='State')
    zip = USZipCodeField(blank=True, null=True, verbose_name='Zip')
    start = models.TimeField(verbose_name='Start')
    end = models.TimeField(verbose_name='End')
    duration = models.PositiveSmallIntegerField(verbose_name='Duration')
    notes = RichTextField(blank=True, null=True, verbose_name='Notes')
    handraises = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated')

    objects = PhoneCallManager()

    def __str__(self):
        return '{} - {}'.format(self.call_date, self.content_object)

    class Meta:
        verbose_name = 'Phone Call'
        verbose_name_plural = 'Phone Calls'
        unique_together = ('call_date', 'email', 'start', 'end', 'duration', )
        ordering = ['-call_date', ]
