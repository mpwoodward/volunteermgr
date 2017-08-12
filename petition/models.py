from localflavor.us.models import USStateField, USZipCodeField

from django.db import models


class PetitionSigner(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='First Name')
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Last Name')
    email = models.EmailField(unique=True, verbose_name='Email')
    city = models.CharField(max_length=250, blank=True, null=True, verbose_name='City')
    state = USStateField(blank=True, null=True, db_index=True, verbose_name='State')
    zip = USZipCodeField(blank=True, null=True, db_index=True, verbose_name='Zip')
    non_conforming_zip = models.CharField(max_length=250, blank=True, null=True, verbose_name='Non-Conforming Zip')
    dt_signed = models.DateTimeField(verbose_name='Signed')

    def __str__(self):
        return '{} - {}'.format(self.email, self.dt_signed)

    class Meta:
        verbose_name = 'Petition Signer'
        verbose_name_plural = 'Petition Signers'
        ordering = ['-dt_signed', 'last_name', 'first_name', ]
