from django.db import models

from ckeditor.fields import RichTextField
from localflavor.us.models import USStateField, USZipCodeField

from security.models import User


class Organization(models.Model):
    key = models.CharField(max_length=20, unique=True, verbose_name='Key')
    name = models.CharField(max_length=250, unique=True, verbose_name='Name')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name', ]


class Category(models.Model):
    key = models.CharField(max_length=20, verbose_name='Key')
    category = models.CharField(max_length=100, verbose_name='Category')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['ordering', ]


class ContactManager(models.Manager):
    def get_contact_if_allowed(self, contact_id, requester):
        if requester.is_superuser:
            return self.get(pk=contact_id)
        else:
            return self.get(
                pk=contact_id,
                state__in=[org.state for org in requester.organizations.all()]
            )

    def get_contacts_for_user(self, requester):
        if requester.is_superuser:
            return self.all()
        else:
            return self.filter(state__in=[org.state for org in requester.organizations.all()])


class Contact(models.Model):
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
    state = USStateField(db_index=True, verbose_name='State')
    zip = USZipCodeField(blank=True, null=True, db_index=True, verbose_name='Zip')
    details = RichTextField(blank=True, null=True, verbose_name='Details')
    categories = models.ManyToManyField(Category, blank=True, verbose_name='Categories')
    facebook_profile = models.URLField(blank=True, null=True, verbose_name='Facebook Profile')
    twitter_profile = models.URLField(blank=True, null=True, verbose_name='Twitter Profile')
    instagram_profile = models.URLField(blank=True, null=True, verbose_name='Instagram Profile')
    reddit_profile = models.URLField(blank=True, null=True, verbose_name='Reddit Profile')
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    objects = ContactManager()

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

    def __str__(self):
        name = '{}, {}'.format(self.last_name, self.first_name)

        if self.preferred_name:
            name += ' ({})'.format(self.preferred_name)

        return name

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['last_name', 'first_name', ]


class Note(models.Model):
    contact = models.ForeignKey(Contact)
    note = RichTextField()
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    created_by = models.ForeignKey(User, blank=True, null=True, verbose_name='Created By',
                                   related_name='note_created_by')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated On')
    updated_by = models.ForeignKey(User, blank=True, null=True, verbose_name='Updated By',
                                   related_name='note_updated_by')

    def __str__(self):
        return '{} ({})'.format(self.contact, self.dt_updated)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['contact', 'dt_updated', ]
