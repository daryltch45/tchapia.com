from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

VERIFICATION_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('verified', 'Verified'),
    ('rejected', 'Rejected'),
]

class Handyman(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='handyman_profile')
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, help_text='Rate per hour in XAF', blank=True, null=True)
    skills = models.TextField(help_text='List your skills separated by commas', blank=True, null=True)
    availability = models.BooleanField(default=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    id_card_number = models.CharField(max_length=50, blank=True, null=True)
    id_card_image = models.ImageField(upload_to='id_cards/', blank=True, null=True)
    portfolio_images = models.TextField(blank=True, null=True, help_text='URLs of portfolio images separated by commas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Handyman"

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0

    @property
    def total_projects(self):
        return self.projects.filter(status='completed').count()

    class Meta:
        db_table = 'handyman_handyman'

class HandymanService(models.Model):
    handyman = models.ForeignKey(Handyman, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey('base.Service', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in XAF')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.handyman.user.first_name} - {self.service.name}"

    class Meta:
        db_table = 'handyman_handymanservice'
        unique_together = ['handyman', 'service']

class HandymanRating(models.Model):
    handyman = models.ForeignKey(Handyman, on_delete=models.CASCADE, related_name='ratings')
    customer = models.ForeignKey('customer.Customer', on_delete=models.CASCADE)
    project = models.ForeignKey('customer.Project', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.handyman.user.first_name} - {self.rating} stars"

    class Meta:
        db_table = 'handyman_handymanrating'
        unique_together = ['handyman', 'customer', 'project']

class ProjectOffer(models.Model):
    OFFER_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('withdrawn', 'Retirée'),
    ]

    handyman = models.ForeignKey(Handyman, on_delete=models.CASCADE, related_name='offers')
    project = models.ForeignKey('customer.Project', on_delete=models.CASCADE, related_name='offers')
    message = models.TextField(help_text='Message d\'accompagnement de votre offre')
    proposed_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text='Budget proposé en XAF', blank=True, null=True)
    estimated_duration = models.CharField(max_length=100, help_text='Durée estimée (ex: 2 jours, 1 semaine)', blank=True, null=True)
    status = models.CharField(max_length=20, choices=OFFER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.handyman.user.first_name} - {self.project.name} - {self.status}"

    class Meta:
        db_table = 'handyman_projectoffer'
        unique_together = ['handyman', 'project']
        ordering = ['-created_at']

class HandymanNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_project', 'New Project'),
        ('project_update', 'Project Update'),
        ('message', 'Message'),
        ('offer_status', 'Offer Status'),
    ]

    handyman = models.ForeignKey(Handyman, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    project = models.ForeignKey('customer.Project', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.handyman.user.first_name} - {self.title}"

    class Meta:
        db_table = 'handyman_notification'
        ordering = ['-created_at']


class HandymanPortfolioImage(models.Model):
    handyman = models.ForeignKey(Handyman, on_delete=models.CASCADE, related_name='portfolio_images_set')
    image = models.ImageField(upload_to='handyman_portfolio/', help_text='Images du portfolio')
    title = models.CharField(max_length=200, blank=True, null=True, help_text='Titre du projet/travail')
    description = models.CharField(max_length=500, blank=True, null=True, help_text='Description du travail réalisé')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.handyman.user.first_name} - Portfolio Image {self.id}"

    class Meta:
        db_table = 'handyman_portfolio_image'
        ordering = ['uploaded_at']
