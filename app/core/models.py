from datetime import date, timedelta
import json

from django.db import models
from django.contrib.auth.models import User
from app.common.constants import BUCKET_FOLDER_NAME
from app.core import constants
from django.conf import settings


class CustomTimeStampModel(models.Model):
    """Custom Timestamp model with is_active status."""

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta for custom timestamp model."""

        abstract = True


class Region(CustomTimeStampModel):
    """Region model."""

    name = models.CharField(max_length=30, unique=True)
    country = models.CharField(
        blank=True, max_length=20, verbose_name='Country')

    @property
    def representation(self):
        """
        Representation for region model.

        :return:
        """
        return f'{self.name} - {self.country}'

    def __str__(self):
        """
        Representation for region model.

        :return:
        """
        return self.representation

    class Meta:
        """Meta for region model."""

        db_table = 'region'


class Area(models.Model):
    """Area model."""
    name = models.CharField(blank=True, max_length=20, verbose_name='Name')
    city = models.CharField(blank=True, max_length=20, verbose_name='City')
    council = models.CharField(
        blank=True, max_length=30, verbose_name='Council')
    region = models.ForeignKey(
        Region, related_name='region', null=True, blank=True, on_delete=models.CASCADE,
    )

    @property
    def representation(self):
        """
        Representation for region model.

        :return:
        """
        return f'{self.name}, {self.city}, {self.region}'

    def __str__(self):
        """
        Representation for region model.

        :return:
        """
        return self.representation

    class Meta:
        """Meta for region model."""

        db_table = 'area'


class RelativesRelation(CustomTimeStampModel):
    """Relatives Relation model."""

    name = models.CharField(max_length=50, unique=True)
    order_by = models.PositiveSmallIntegerField(unique=True)

    @property
    def representation(self):
        """
        Return string representation of RelativesRelation objects.

        :return:
        """
        return self.name

    def __str__(self):
        """
        Return string representation of RelativesRelation objects.

        :return:
        """
        return self.representation

    class Meta:
        """Meta for Relative Relation model."""

        db_table = 'relatives_relation'
        verbose_name = 'Relatives Relation'
        verbose_name_plural = 'Relatives Relations'
        ordering = ['order_by']


class UserProfile(models.Model):
    """User profile model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    full_name = models.CharField(max_length=100, db_index=True)
    fathers_name = models.CharField(max_length=30, null=True, blank=True)
    personal_email = models.EmailField(max_length=70, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nic = models.CharField(
        max_length=20, unique=True, verbose_name='CNIC', help_text='National ID number', null=True
    )
    gender = models.CharField(
        max_length=1, choices=constants.GENDER_CHOICES, blank=True
    )
    marital_status = models.IntegerField(
        choices=constants.MARITAL_STATUS_CHOICES, default=constants.SINGLE,
    )
    cellphone_number = models.CharField(null=True, blank=True, max_length=30)
    whatsapp_cellphone_number = models.CharField(
        null=True, blank=True, max_length=30
    )
    emergency_contact_name = models.CharField(
        null=True, blank=True, max_length=50,
    )
    emergency_contact_number = models.CharField(
        null=True, blank=True, max_length=20,
    )
    emergency_contact_relation = models.ForeignKey(
        RelativesRelation, related_name='person', null=True, blank=True, on_delete=models.CASCADE,
    )
    current_address = models.CharField(blank=True, max_length=150)
    permanent_address = models.CharField(blank=True, max_length=150)
    city = models.CharField(
        blank=True, max_length=20, verbose_name='Belonging City'
    )

    @property
    def gender_name(self):
        """
        Return the gender name of given instance.

        :return:
        """
        return dict(constants.GENDER_CHOICES).get(self.gender)

    @property
    def marital_status_name(self):
        """
        Return the marital_status name of given instance.

        :return:
        """
        return dict(constants.MARITAL_STATUS_CHOICES).get(self.marital_status)

    @property
    def representation(self):
        """
        Representation for user profile model.

        :return:
        """
        return self.full_name

    def __str__(self):
        """
        Representation for user profile model.

        :return:
        """
        return self.representation

    class Meta:
        """Meta for user profile model."""

        db_table = 'user_profile'
        abstract = True


def avatar_uploading_path(instance, filename=''):
    """
    Avatar uploading path.

    :param instance:
    :param filename:
    :return:
    """
    return f'{instance.person_id}/Personal_Docs/{BUCKET_FOLDER_NAME}/{filename}'

# Add Cache here

# pylint: disable=no-member
class Person(UserProfile):
    """Person model."""

    person_id = models.CharField(
        max_length=20, unique=True, verbose_name='Person ID')

    area = models.ForeignKey(Area, related_name='area',
                             on_delete=models.CASCADE)

    avatar = models.ImageField(
        upload_to=avatar_uploading_path, verbose_name='Profile Picture', null=True, blank=True, max_length=200)
    thumbnail = models.ImageField(
        upload_to=avatar_uploading_path, verbose_name='Profile Thumbnail', null=True, blank=True, max_length=200)

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_loggable = models.BooleanField(default=True)

    @property
    def is_single(self):
        """
        Check if person is single or not.

        :return:
        """
        return self.marital_status == constants.SINGLE

    @property
    def is_male(self):
        """
        Check if person is male or not.

        :return:
        """
        return self.gender == 'M'

    @property
    def gender_specific_pronoun(self):
        """
        Gender based pronoun.

        :return:
        """
        return 'He' if self.is_male else 'She'

    @property
    def child_gender_abbreviation(self):
        """
        Child Gender Abbreviation.

        :return:
        """
        return 's/o' if self.is_male else 'd/o'

    @property
    def gender_pronoun(self):
        """
        Gender Pronoun.

        :return:
        """
        return 'him' if self.is_male else 'her'

    @property
    def gender_title(self):
        """
        Gender Title.

        :return:
        """
        return 'Mr' if self.is_male else 'Ms'

    @property
    def gender_possessive_pronoun(self):
        """
        Gender Possessive Pronoun.

        :return:
        """
        return 'his' if self.is_male else 'her'

    @property
    def unique_name(self):
        """
        Person complete name with employee id.

        :return:
        """
        return f'{self.full_name} - {self.person_id}'

    @property
    def representation(self):
        """
        Representation of person Model.

        :return:
        """
        return self.full_name

    def __str__(self):
        """
        Representation of person Model.

        :return:
        """
        return self.unique_name

    class Meta:
        """Meta for person model."""

        db_table = 'person'
        verbose_name_plural = 'People'
        ordering = ['full_name']
        permissions = (

        )
