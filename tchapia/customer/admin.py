from django.contrib import admin
from .models import Customer, Project

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_payment_method', 'mobile_money_number', 'created_at']
    list_filter = ['preferred_payment_method', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'service', 'handyman', 'status', 'priority', 'budget_range', 'city', 'created_at']
    list_filter = ['service', 'status', 'priority', 'region', 'created_at']
    search_fields = ['name', 'description', 'customer__user__first_name', 'handyman__user__first_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
