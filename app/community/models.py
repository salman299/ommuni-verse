from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

from app.core.models import Area
from app.community.constants import PaymentStatus

class BaseAuditModel(models.Model):
    """
    BaseAudit Model
    This is an abstract base model that provides audit fields for tracking
    when a model instance was created, updated, and by which user.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='%(class)s_created', on_delete=models.SET_NULL, null=True, blank=True)
    updated_by = models.ForeignKey(
        User, related_name='%(class)s_updated', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True


class Community(BaseAuditModel):
    """
    Community Model
    This model represents a community within the application.
    It stores the name, description, and visibility settings of the community.
    """
    slug = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(5)])
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Communities'


class CommunityDetail(models.Model):
    """
    Community Detail Model
    This model stores additional details about a community, such as
    additional information and rules.
    """
    community = models.OneToOneField(
        Community, on_delete=models.CASCADE, related_name='detail')
    additional_info = models.TextField(blank=True)
    rules = models.TextField(blank=True)

    def __str__(self):
        return f'Detail of {self.community.name}'

    class Meta:
        verbose_name_plural = 'Community Details'


class CommunityMembership(models.Model):
    """
    Community Membership Model
    This model represents a user's membership in a community, including
    their role (owner, manager, or member).
    """
    OWNER = 'owner'
    MANAGER = 'manager'
    MEMBER = 'member'

    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (MANAGER, 'Manager'),
        (MEMBER, 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'community')
        verbose_name_plural = 'Community Memberships'

    def __str__(self):
        return f'{self.user.username} in {self.community.name} as {self.role}'


class CommunityJoinRequest(models.Model):
    """
    Community Join Request Model
    This model represents a request from a user to join a community.
    It stores the user, community, and whether the request has been approved.
    """
    PENDING = 'pending'
    APPROVED = 'approved'
    DECLINED = 'declined'

    JOIN_REQUEST_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'APPROVED'),
        (DECLINED, 'DECLINED'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='join_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=JOIN_REQUEST_STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f'Join request by {self.user.username} to {self.community.name}'

    class Meta:
        verbose_name_plural = 'Community Join Requests'


class Event(BaseAuditModel):
    """
    Event Model
    This model represents an event organized by a community.
    It stores details such as name, description, organizer, fees, and currency.
    """
    PKR = 'PKR'
    USD = 'USD'

    CURRENCY_CHOICES = [
        (PKR, 'PKR'),
        (USD, 'USD'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    organized_by = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='events')
    is_free = models.BooleanField(default=False)
    fees = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default=PKR)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Events'


class EventCollaboration(models.Model):
    """
    Event Collaboration Model
    This model represents a collaboration between communities for an event.
    It stores the event, the collaborating community, and the status of the collaboration.
    """
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELED = 'canceled'

    COLLABORATION_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (CANCELED, 'Canceled'),
    ]

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='collaborations')
    collaborating_community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name='event_collaborations')
    status = models.CharField(
        max_length=20, choices=COLLABORATION_STATUS_CHOICES, default=PENDING)

    class Meta:
        unique_together = ('event', 'collaborating_community')
        verbose_name_plural = 'Event Collaborations'

    def __str__(self):
        return f'Collaboration for {self.event.name} with {self.collaborating_community.name}'


class EventRegistration(models.Model):
    """
    Event Registration Model
    This model represents a user's registration for an event.
    It stores the user, event, and registration details.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.PAYMENT_STATUS_CHOICES, default=PaymentStatus.NOT_APPLICABLE)

    def __str__(self):
        return f'{self.user.username} registered for {self.event.name}'

    class Meta:
        verbose_name_plural = 'Event Registrations'


class Payment(models.Model):
    """
    Payment Model
    This model represents a payment made for an event registration.
    It stores the payment details, including the payment method and proof of payment.
    """

    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('on_hand', 'On Hand'),
    ]

    registration = models.OneToOneField(
        EventRegistration, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proof_of_payment = models.ImageField(
        upload_to='payment_proofs', null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.PAYMENT_STATUS_CHOICES, default=PaymentStatus.PENDING)
    note = models.TextField()

    def __str__(self):
        return f'Payment for {self.registration.event.name} by {self.registration.user.username}'

    class Meta:
        verbose_name_plural = 'Payments'
