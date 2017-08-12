from django.db import models

from ckeditor.fields import RichTextField
from localflavor.us.models import USStateField, USZipCodeField

from contact.models import Contact
from organization.models import Organization


class Event(models.Model):
    organization = models.ForeignKey(Organization, verbose_name='Organization')
    name = models.CharField(max_length=250, verbose_name='Name')
    dt_start = models.DateTimeField(verbose_name='Date/Time Starts', db_index=True)
    dt_end = models.DateTimeField(blank=True, null=True, verbose_name='Date/Time Ends')
    location = models.CharField(max_length=250, blank=True, null=True)
    address_1 = models.CharField(max_length=250, blank=True, null=True)
    address_2 = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    state = USStateField(blank=True, null=True)
    zip = USZipCodeField(blank=True, null=True)
    details = RichTextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True, verbose_name='URL')
    contact = models.ForeignKey(Contact, blank=True, null=True, related_name='event_contact')
    attendees = models.ManyToManyField(Contact, related_name='attendees')

    def __str__(self):
        start = self.dt_start.strftime('%m/%d/%Y')
        return '{}: {} ({})'.format(start, self.name, self.organization)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-dt_start', 'organization', ]
