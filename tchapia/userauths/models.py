from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

REGION_CHOICES = [
    ('adamawa', 'Adamawa'),
    ('centre', 'Centre'),
    ('east', 'East'),
    ('far_north', 'Far North'),
    ('littoral', 'Littoral'),
    ('north', 'North'),
    ('northwest', 'Northwest'),
    ('south', 'South'),
    ('southwest', 'Southwest'),
    ('west', 'West'),
]

USER_TYPE_CHOICES = [
    ('customer', 'Customer'),
    ('handyman', 'Handyman'),
    ('admin', 'Admin'),
]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    bio = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=20, choices=REGION_CHOICES)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'city', 'region']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    class Meta:
        db_table = 'userauths_user'

