from django.db import models
from django.conf import settings

# Create your models here.

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
]

PAYMENT_METHOD_CHOICES = [
    ('mtn_momo', 'MTN Mobile Money'),
    ('orange_money', 'Orange Money'),
    ('bank_transfer', 'Bank Transfer'),
    ('cash', 'Cash'),
]

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'base_service'

class Billing(models.Model):
    project = models.ForeignKey('customer.Project', on_delete=models.CASCADE, related_name='billings')
    handyman = models.ForeignKey('handyman.Handyman', on_delete=models.CASCADE)
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Billing #{self.id} - {self.amount} XAF"

    class Meta:
        db_table = 'base_billing'

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    project = models.ForeignKey('customer.Project', on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey('base.Service', on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.type}"

    class Meta:
        db_table = 'base_notification'
        ordering = ['-created_at']