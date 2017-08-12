from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from ckeditor.fields import RichTextField
from localflavor.us.models import USStateField, USZipCodeField

from gis.models import ZipCode
from organization.models import Organization
from petition.models import PetitionSigner
from security.models import User


class Category(models.Model):
    key = models.CharField(max_length=20, unique=True, verbose_name='Key')
    category = models.CharField(max_length=100, unique=True, verbose_name='Category')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['ordering', ]


class VolunteerSource(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name='Key')
    source = models.CharField(max_length=100, unique=True, verbose_name='Source')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.source

    class Meta:
        verbose_name = 'Volunteer Source'
        verbose_name_plural = 'Volunteer Sources'
        ordering = ['ordering', ]


class VolunteerActivity(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name='Key')
    activity_short = models.CharField(max_length=50, unique=True, verbose_name='Activity (Short)')
    activity = models.CharField(max_length=500, unique=True, verbose_name='Activity (Full)')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.activity_short

    class Meta:
        verbose_name = 'Volunteer Activity'
        verbose_name_plural = 'Volunteer Activities'
        ordering = ['ordering', ]


class VolunteerManager(models.Manager):
    def get_volunteers_for_user(self, requester):
        if requester.is_superuser:
            return self.all()
        else:
            return self.filter(
                organization__id__in=[org.id for org in requester.organizations.all()]
            )

    def get_volunteer_if_allowed(self, volunteer_id, requester):
        if requester.is_superuser:
            return self.get(pk=volunteer_id)
        else:
            return self.get(
                pk=volunteer_id,
                organization__in=[org for org in requester.organizations.all()]
            )


class Volunteer(models.Model):
    organization = models.ForeignKey(Organization, blank=True, null=True, db_index=True, verbose_name='Organization')
    first_name = models.CharField(max_length=100, db_index=True, verbose_name='First Name')
    preferred_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Preferred Name')
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Middle Name')
    last_name = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name='Last Name')
    suffix = models.CharField(max_length=20, blank=True, null=True, verbose_name='Suffix')
    email = models.EmailField(max_length=250, unique=True, db_index=True, verbose_name='Email')
    phone = models.CharField(max_length=100, blank=True, null=True, verbose_name='Phone')
    address_1 = models.CharField(max_length=250, blank=True, null=True, verbose_name='Address')
    address_2 = models.CharField(max_length=250, blank=True, null=True, verbose_name='Address (cont.)')
    city = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name='City')
    state = USStateField(blank=True, null=True, db_index=True, verbose_name='State')
    zip = USZipCodeField(blank=True, null=True, db_index=True, verbose_name='Zip')
    details = RichTextField(blank=True, null=True, verbose_name='Details')
    categories = models.ManyToManyField(Category, blank=True, verbose_name='Categories')
    dt_signed_petition = models.DateTimeField(blank=True, null=True, verbose_name='Signed Petition')
    date_signed_up = models.DateField(blank=True, null=True, verbose_name='Date Signed Up')
    date_contacted = models.DateField(blank=True, null=True, verbose_name='Date Contacted')
    contacted_by = models.CharField(max_length=250, blank=True, null=True, verbose_name='Contacted By')
    volunteer_commitment = models.CharField(max_length=250, blank=True, null=True, verbose_name='Volunteer Commitment')
    volunteer_activities = models.ManyToManyField(VolunteerActivity, blank=True, verbose_name='Volunteer Activities')
    volunteer_other = RichTextField(blank=True, null=True, verbose_name='Volunteer Other')
    previous_organizing_experience = RichTextField(blank=True, null=True, verbose_name='Previous Organizing Experience')
    active_in_presidential_primary = RichTextField(blank=True, null=True, verbose_name='Active in Presidential Primary')
    other_skills = RichTextField(blank=True, null=True, verbose_name='Other Skills')
    facebook_profile = models.URLField(blank=True, null=True, verbose_name='Facebook Profile')
    twitter_profile = models.URLField(blank=True, null=True, verbose_name='Twitter Profile')
    instagram_profile = models.URLField(blank=True, null=True, verbose_name='Instagram Profile')
    reddit_profile = models.URLField(blank=True, null=True, verbose_name='Reddit Profile')
    volunteer_comments = RichTextField(blank=True, null=True, verbose_name='Volunteer Comments')
    sources = models.ManyToManyField(VolunteerSource, blank=True, verbose_name='Sources')
    date_added_to_list = models.DateField(blank=True, null=True, verbose_name='Date Added To List')
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    phonecalls = GenericRelation('phonecall.PhoneCall', related_query_name='volunteer_phonecalls')

    objects = VolunteerManager()

    def save(self, *args, **kwargs):
        # try to get their city and state if needed based on zip
        if self.zip and (not self.city or not self.state):
            try:
                vzip = self.zip
                if '-' in vzip:
                    vzip = vzip.split('-')[0]

                zip_code = ZipCode.objects.get(zip=vzip)
                self.city = zip_code.city
                self.state = zip_code.state
            except ZipCode.DoesNotExist:
                pass  # we tried!

        # if they signed the petition, add that info
        if not self.dt_signed_petition:
            try:
                ps = PetitionSigner.objects.get(email__iexact=self.email)
                self.dt_signed_petition = ps.dt_signed
            except PetitionSigner.DoesNotExist:
                pass  # haven't signed

        super(Volunteer, self).save(*args, **kwargs)

    @property
    def full_name(self):
        name = self.first_name

        if self.middle_name:
            name += ' {}'.format(self.middle_name)

        name += ' {}'.format(self.last_name)

        if self.suffix:
            name += ' {}'.format(self.suffix)

        return name

    @property
    def short_name(self):
        if self.preferred_name:
            name = self.preferred_name
        else:
            name = self.first_name

        name += ' {}'.format(self.last_name)

        return name

    @property
    def signed_petition(self):
        if self.dt_signed_petition:
            return True
        else:
            return False

    def __str__(self):
        name = '{}, {}'.format(self.last_name, self.first_name)

        if self.preferred_name:
            name += ' ({})'.format(self.preferred_name)

        return name

    class Meta:
        verbose_name = 'Volunteer'
        verbose_name_plural = 'Volunteers'
        ordering = ['last_name', 'first_name', ]


class Note(models.Model):
    volunteer = models.ForeignKey(Volunteer)
    note = RichTextField()
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    created_by = models.ForeignKey(User, blank=True, null=True, verbose_name='Created By',
                                   related_name='volunteer_note_created_by')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    updated_by = models.ForeignKey(User, blank=True, null=True, verbose_name='Updated By',
                                   related_name='volunteer_note_updated_by')

    def __str__(self):
        return '{} ({})'.format(self.volunteer, self.dt_updated)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['volunteer', 'dt_updated', ]
