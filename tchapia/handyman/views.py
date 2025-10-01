from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from customer.models import Project
from .models import Handyman
from .forms import HandymanProfileForm, UserProfileForm

@login_required
def projects_view(request):
    # Ensure user is a handyman
    if request.user.user_type != 'artisan':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux artisans.")
        return redirect('base:home')

    # Get or create handyman profile
    handyman, created = Handyman.objects.get_or_create(user=request.user)

    # Get projects that match the handyman's service and region
    projects = Project.objects.filter(
        service=request.user.service,
        region=request.user.region,
        status__in=['published', 'in_progress']
    ).order_by('-created_at')

    # Get project count by status
    total_projects = projects.count()
    published_projects = projects.filter(status='published').count()
    in_progress_projects = projects.filter(status='in_progress').count()

    context = {
        'handyman': handyman,
        'projects': projects,
        'total_projects': total_projects,
        'published_projects': published_projects,
        'in_progress_projects': in_progress_projects,
    }
    return render(request, 'handyman/projects.html', context)

@login_required
def profile_edit_view(request):
    # Ensure user is a handyman
    if request.user.user_type != 'artisan':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux artisans.")
        return redirect('base:home')

    # Get or create handyman profile
    handyman, created = Handyman.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        handyman_form = HandymanProfileForm(request.POST, request.FILES, instance=handyman)

        if user_form.is_valid() and handyman_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    handyman_form.save()
                    messages.success(request, "Profil mis à jour avec succès!")
                    return redirect('handyman:profile_edit')
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    else:
        user_form = UserProfileForm(instance=request.user)
        handyman_form = HandymanProfileForm(instance=handyman)

    context = {
        'user_form': user_form,
        'handyman_form': handyman_form,
        'handyman': handyman,
    }
    return render(request, 'handyman/profile_edit.html', context)
