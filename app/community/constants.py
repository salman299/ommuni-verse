"""
Constants for the community app.
"""

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
