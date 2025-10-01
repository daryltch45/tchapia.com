from django.shortcuts import render
from handyman import models as handyman_models
from userauths.models import REGION_CHOICES, SERVICE_CHOICES 

def home_view(request):

    print("########## Current User: ", request.user)
    context = {
        "user": request.user
    }
    return render(request, 'base/home.html', context)


def handymen_list_view(request):
    handymen = handyman_models.Handyman.objects.select_related('user').all()

    # Get filter parameters
    service_filter = request.GET.get('service', '')
    region_filter = request.GET.get('region', '')
    city_filter = request.GET.get('city', '')
    availability_filter = request.GET.get('availability', '')

    # Apply filters
    if service_filter:
        handymen = handymen.filter(user__service=service_filter)

    if region_filter:
        handymen = handymen.filter(user__region=region_filter)

    if city_filter:
        handymen = handymen.filter(user__city__icontains=city_filter)

    if availability_filter == 'available':
        handymen = handymen.filter(availability=True)
    elif availability_filter == 'unavailable':
        handymen = handymen.filter(availability=False)

    # Order by verification status and rating
    handymen = handymen.order_by('verification_status', '-created_at')

    context = {
        "handymen": handymen,
        "current_service": service_filter,
        "current_region": region_filter,
        "current_city": city_filter,
        "current_availability": availability_filter,
        "service_choices": SERVICE_CHOICES,
        "region_choices": REGION_CHOICES,
        "handymen_count": handymen.count(),
    }

    return render(request, "base/handymen_list.html", context)


def services_list_view(request):
    # Get service statistics - count of artisans per service
    services_with_counts = []
    for service_code, service_name in SERVICE_CHOICES:
        artisan_count = handyman_models.Handyman.objects.filter(
            user__service=service_code
        ).count()
        services_with_counts.append({
            'code': service_code,
            'name': service_name,
            'count': artisan_count
        })

    context = {
        'services_with_counts': services_with_counts,
        'service_choices': SERVICE_CHOICES,
    }

    return render(request, "base/services_list.html", context)
