from localflavor.us.models import USStateField, USZipCodeField

from django.db import models


class ZipCode(models.Model):
    zip = USZipCodeField(db_index=True, verbose_name='Zip')
    state = USStateField(db_index=True, verbose_name='State')
    city = models.CharField(max_length=250, verbose_name='City')
    county = models.CharField(blank=True, null=True, max_length=250, verbose_name='County')
    lat = models.FloatField(blank=True, null=True, verbose_name='Latitude')
    long = models.FloatField(blank=True, null=True, verbose_name='Longitude')

    def __str__(self):
        return '{}, {} {}'.format(self.city, self.state, self.zip)

    class Meta:
        verbose_name = 'Zip Code'
        verbose_name_plural = 'Zip Codes'
        ordering = ['zip', ]
