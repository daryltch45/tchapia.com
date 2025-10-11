from django.contrib import admin
from .models import Handyman, HandymanService, HandymanRating

@admin.register(Handyman)
class HandymanAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_years', 'hourly_rate', 'availability', 'verification_status', 'created_at']
    list_filter = ['availability', 'verification_status', 'experience_years', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'skills']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(HandymanService)
class HandymanServiceAdmin(admin.ModelAdmin):
    list_display = ['handyman', 'service', 'price', 'created_at']
    list_filter = ['service', 'created_at']
    search_fields = ['handyman__user__first_name', 'handyman__user__last_name', 'service__name']
    ordering = ['-created_at']

@admin.register(HandymanRating)
class HandymanRatingAdmin(admin.ModelAdmin):
    list_display = ['handyman', 'customer', 'project', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['handyman__user__first_name', 'customer__user__first_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']