from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Message
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

# ...existing code...

@login_required
def inbox_view(request):
    user = request.user
    # Get all users who have messaged or been messaged by this user
    contacts = set()
    sent = Message.objects.filter(sender=user).values_list('receiver', flat=True)
    received = Message.objects.filter(receiver=user).values_list('sender', flat=True)
    contacts.update(sent)
    contacts.update(received)
    User = get_user_model()
    contacts = User.objects.filter(id__in=contacts)
    return render(request, 'base/inbox.html', {'contacts': contacts})

@login_required
def conversation_view(request, user_id):
    user = request.user
    other_user = get_user_model().objects.get(id=user_id)
    messages = Message.objects.filter(
        (Q(sender=user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=user))
    ).order_by('timestamp')
    # Mark received messages as read
    messages.filter(receiver=user, is_read=False).update(is_read=True)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=user, receiver=other_user, content=content)
            return HttpResponseRedirect(reverse('base:conversation', args=[other_user.id]))
    return render(request, 'base/conversation.html', {'messages': messages, 'other_user': other_user})
from django.shortcuts import render, get_object_or_404
from handyman import models as handyman_models
from userauths.models import REGION_CHOICES, SERVICE_CHOICES, CITIES 

def home_view(request):

    print(f"########## Current User: {request.user} ######")
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
    verified_filter = request.GET.get('verified', '')

    # Apply filters
    if service_filter:
        handymen = handymen.filter(user__service=service_filter)

    if region_filter:
        handymen = handymen.filter(user__region=region_filter)

    if city_filter:
        handymen = handymen.filter(user__city=city_filter)

    if verified_filter == 'verified':
        handymen = handymen.filter(verification_status="verified")
    elif verified_filter == 'pending':
        handymen = handymen.filter(verification_status="pending")

    # Order by verification status and rating
    handymen = handymen.order_by('verification_status', '-created_at')

    context = {
        "handymen": handymen,
        "current_service": service_filter,
        "current_region": region_filter,
        "current_city": city_filter,
        "verified_filter": verified_filter,
        "service_choices": SERVICE_CHOICES,
        "region_choices": REGION_CHOICES,
        "cities": CITIES,
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


def handyman_profile_view(request, handyman_id):
    handyman = get_object_or_404(handyman_models.Handyman, id=handyman_id)

    # Get handyman's ratings and reviews
    ratings = handyman.ratings.all().order_by('-created_at')

    # Get recent projects (if any)
    recent_projects = handyman.projects.filter(status__in=['completed', 'in_progress']).order_by('-created_at')[:3]

    context = {
        'handyman': handyman,
        'ratings': ratings,
        'recent_projects': recent_projects,
        'ratings_count': ratings.count(),
        'average_rating': handyman.average_rating,
    }

    return render(request, "base/handyman_profile.html", context)
