from django.db import models
from django.conf import settings

# Create your models here.

PROJECT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    preferred_payment_method = models.CharField(max_length=20, blank=True, null=True)
    mobile_money_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Customer"

    @property
    def total_projects(self):
        return self.projects.count()

    @property
    def completed_projects(self):
        return self.projects.filter(status='completed').count()

    class Meta:
        db_table = 'customer_customer'

class Project(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    handyman = models.ForeignKey('handyman.Handyman', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, help_text='Minimum budget in XAF')
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, help_text='Maximum budget in XAF')
    location_address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    images = models.TextField(blank=True, null=True, help_text='URLs of project images separated by commas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.customer.user.first_name}"

    @property
    def budget_range(self):
        return f"{self.budget_min:,.0f} - {self.budget_max:,.0f} XAF"

    @property
    def is_active(self):
        return self.status in ['published', 'in_progress']

    class Meta:
        db_table = 'customer_project'
        ordering = ['-created_at']

class ProjectService(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey('base.Service', on_delete=models.CASCADE)
    requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.service.name}"

    class Meta:
        db_table = 'customer_projectservice'
        unique_together = ['project', 'service']
