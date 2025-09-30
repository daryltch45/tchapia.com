from django.contrib import admin
from .models import Customer, Project, ProjectService

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_payment_method', 'mobile_money_number', 'created_at']
    list_filter = ['preferred_payment_method', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'handyman', 'status', 'priority', 'budget_range', 'city', 'created_at']
    list_filter = ['status', 'priority', 'region', 'created_at']
    search_fields = ['name', 'description', 'customer__user__first_name', 'handyman__user__first_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProjectService)
class ProjectServiceAdmin(admin.ModelAdmin):
    list_display = ['project', 'service', 'created_at']
    list_filter = ['service', 'created_at']
    search_fields = ['project__name', 'service__name']
    ordering = ['-created_at']
