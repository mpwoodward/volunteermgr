from ckeditor.fields import RichTextField

from localflavor.us.models import PhoneNumberField
from localflavor.us.models import USStateField
from localflavor.us.models import USZipCodeField

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from organization.models import Organization


class AccountType(models.Model):
    key = models.CharField(max_length=20, verbose_name='Key')
    type = models.CharField(max_length=100, verbose_name='Type')
    permission_hierarchy = models.PositiveSmallIntegerField(verbose_name='Permission Hierarchy')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'Account Type'
        verbose_name_plural = 'Account Types'
        ordering = ['ordering', ]


class Position(models.Model):
    position = models.CharField(max_length=100, verbose_name='Position')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.position

    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['ordering', ]


class Team(models.Model):
    team = models.CharField(max_length=100, verbose_name='Team')
    ordering = models.PositiveSmallIntegerField(verbose_name='Ordering')

    def __str__(self):
        return self.team

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['ordering', ]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        if extra_fields.get('is_superuser', False):
            raise ValueError('Superuser must have is_superuser set to True')

        return self._create_user(email, password, **extra_fields)

    def get_user_if_allowed(self, id, requester):
        if requester.is_superuser:
            return self.get(pk=id)
        elif requester.account_type:
            return self.get(
                pk=id,
                organizations__in=[org.id for org in requester.organizations.all()],
                account_type__permission_hierarchy__gt=requester.account_type.permission_hierarchy,
            )
        else:
            raise User.DoesNotExist


class User(AbstractBaseUser, PermissionsMixin):
    account_type = models.ForeignKey(AccountType, blank=True, null=True, verbose_name='Account Type')
    email = models.EmailField(unique=True, db_index=True, verbose_name='Email')
    organizations = models.ManyToManyField(Organization, blank=True, verbose_name='Organizations')
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    phone = PhoneNumberField(blank=True, null=True, verbose_name='Phone')
    city = models.CharField(max_length=250, blank=True, null=True, verbose_name='City')
    state = USStateField(db_index=True, blank=True, null=True, verbose_name='State')
    zip = USZipCodeField(blank=True, null=True, verbose_name='Zip')
    teams = models.ManyToManyField(Team, blank=True, verbose_name='Teams')
    start_date = models.DateField(blank=True, null=True, verbose_name='Start Date')
    end_date = models.DateField(blank=True, null=True, verbose_name='End Date')
    assigned_to = models.CharField(max_length=250, blank=True, null=True, verbose_name='Assigned To')
    campus_lead = models.BooleanField(default=False, verbose_name='Campus Lead')
    facebook_moderator = models.BooleanField(default=False, verbose_name='Facebook Moderator')
    date_welcome_packet_sent = models.DateField(blank=True, null=True, verbose_name='Date Welcome Packet Sent')
    invited_to_slack = models.BooleanField(default=False, verbose_name='Invited to Slack')
    sent_nda = models.BooleanField(default=False, verbose_name='Sent NDA')
    returned_nda = models.BooleanField(default=False, verbose_name='Returned NDA')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff',
                                   help_text='Designates that this user has access to the Django admin')
    is_superuser = models.BooleanField(default=False, verbose_name='Is Superuser',
                                       help_text='Designates that this user has access to all organizations')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    comments = RichTextField(blank=True, null=True, verbose_name='Comments')
    created_by = models.ForeignKey('self', null=True, verbose_name='Created By', related_name='user_created_by')
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated_by = models.ForeignKey('self', null=True, verbose_name='Updated By', related_name='user_updated_by')
    dt_updated = models.DateTimeField(auto_now=True, verbose_name='Updated')
    dt_last_login = models.DateTimeField(blank=True, null=True, verbose_name='Last Login')
    password_reset = models.BooleanField(default=False, verbose_name='Password Reset')
    phonecalls = GenericRelation('phonecall.PhoneCall', related_query_name='user_phonecalls')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return '{}, {}'.format( self.last_name, self.first_name)

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['last_name', 'first_name', ]
