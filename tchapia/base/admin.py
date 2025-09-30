from django.contrib import admin
from .models import Service, Billing, Notification

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'handyman', 'customer', 'amount', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['payment_method', 'payment_status', 'created_at']
    search_fields = ['transaction_id', 'mobile_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'project', 'service', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__email', 'type']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
