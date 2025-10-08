from django.db import models
from django.conf import settings
from userauths.models import SERVICE_CHOICES, REGION_CHOICES, CITIES

# Create your models here.

PROJECT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PRIORITY_CHOICES = [
    ('low', 'Faible'),
    ('medium', 'Moyenne'),
    ('high', 'Haute'),
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
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='plumbing')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, help_text='Minimum budget in XAF', blank=True, null=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, help_text='Maximum budget in XAF', blank=True, null=True)
    location_address = models.TextField()
    city = models.CharField(max_length=100, choices=CITIES, blank=True, null=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
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
        # Handle both None and 0 as "no budget specified"
        min_budget = self.budget_min if self.budget_min and self.budget_min > 0 else None
        max_budget = self.budget_max if self.budget_max and self.budget_max > 0 else None

        if min_budget and max_budget:
            return f"{min_budget:,.0f} - {max_budget:,.0f} XAF"
        elif min_budget:
            return f"À partir de {min_budget:,.0f} XAF"
        elif max_budget:
            return f"Jusqu'à {max_budget:,.0f} XAF"
        else:
            return "Budget à négocier"

    @property
    def is_active(self):
        return self.status in ['published', 'in_progress']

    class Meta:
        db_table = 'customer_project'
        ordering = ['-created_at']


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_images')
    image = models.ImageField(upload_to='project_images/', help_text='Images du projet')
    description = models.CharField(max_length=200, blank=True, null=True, help_text='Description de l\'image')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - Image {self.id}"

    class Meta:
        db_table = 'customer_project_image'
        ordering = ['uploaded_at']


class CustomerNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_offer', 'New Offer'),
        ('offer_update', 'Offer Update'),
        ('project_update', 'Project Update'),
        ('message', 'Message'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    offer = models.ForeignKey('handyman.ProjectOffer', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.first_name} - {self.title}"

    class Meta:
        db_table = 'customer_notification'
        ordering = ['-created_at']

