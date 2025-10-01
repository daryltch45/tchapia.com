from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary in templates"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def get_count(service_stats, service_code):
    """Get artisan count for a service"""
    if service_stats and service_code in service_stats:
        return service_stats[service_code]['count']
    return 0