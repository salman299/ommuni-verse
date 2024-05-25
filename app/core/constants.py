"""Module for core app constants."""

# Sexes
MALE = 'M'
FEMALE = 'F'
NOT_TO_BE_DISCLOSED = 'N'
MALE_WORD = 'Male'
FEMALE_WORD = 'Female'
NOT_TO_BE_DISCLOSED_WORD = 'Not to be disclosed'
GENDER_CHOICES = (
    (MALE, MALE_WORD),
    (FEMALE, FEMALE_WORD),
    (NOT_TO_BE_DISCLOSED, NOT_TO_BE_DISCLOSED_WORD),
)
GENDER_LIST = [
    MALE, FEMALE,
]

# Marital statuses
SINGLE = 1
MARRIED = 2
DIVORCED = 3
WIDOWED = 4
MARITAL_STATUS_CHOICES = (
    (SINGLE, 'Single'),
    (MARRIED, 'Married'),
    (DIVORCED, 'Divorced'),
    (WIDOWED, 'Widowed'),
)
