"""Module for constants."""
from enum import Enum

from datetime import date

from django.conf import settings
from rest_framework.exceptions import ErrorDetail



class PaymentStatus:
    """
    Payment Status Class
    """
    NOT_APPLICABLE = 'N/A'
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'

    PAYMENT_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (FAILED,  'Failed'),
        (REFUNDED, 'Refunded'),
    ]

class Constants:
    """Constant class."""

# Links


# Profile Pic properties
BUCKET_FOLDER_NAME = 'Profile_Pics'
PROFILE_IMAGE_SIZE = (720, 720)
PROFILE_THUMBNAIL_SIZE = (58, 58)
PROFILE_DEFAULT_IMAGE_NAME = 'profile_pic_'
PROFILE_DEFAULT_THUMBNAIL_NAME = 'profile_thumb_'

AVG_DAYS_IN_MONTH = 30.417
AVG_DAYS_IN_YEARS = 365.2425
MONTHS_IN_YEAR = 12
AVG_HOURS_IN_MONTH = 160
AVG_HOURS_IN_DAY = 8
