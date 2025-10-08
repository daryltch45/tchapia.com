from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from customer.models import Project, CustomerNotification
from .models import Handyman, ProjectOffer
from .forms import HandymanProfileForm, UserProfileForm, ProjectOfferForm


def create_customer_notification(customer, notification_type, title, message, project=None, offer=None):
    """Helper function to create customer notifications"""
    CustomerNotification.objects.create(
        customer=customer,
        notification_type=notification_type,
        title=title,
        message=message,
        project=project,
        offer=offer
    )


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


@login_required
def project_detail_view(request, project_id):
    # Ensure user is a handyman
    if request.user.user_type != 'artisan':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux artisans.")
        return redirect('base:home')

    # Get or create handyman profile
    handyman, created = Handyman.objects.get_or_create(user=request.user)

    # Get the project
    project = get_object_or_404(Project, id=project_id)

    # Check if handyman can view this project (same service and region)
    if (project.service != request.user.service or
        project.region != request.user.region):
        messages.error(request, "Vous ne pouvez pas voir ce projet car il ne correspond pas à votre service ou région.")
        return redirect('handyman:projects')

    # Check if handyman has already applied or is assigned to this project
    is_assigned = project.handyman == handyman

    # Check if handyman has already made an offer
    existing_offer = ProjectOffer.objects.filter(handyman=handyman, project=project).first()

    context = {
        'project': project,
        'handyman': handyman,
        'is_assigned': is_assigned,
        'existing_offer': existing_offer,
    }

    return render(request, 'handyman/project_detail.html', context)


@login_required
def submit_offer_view(request, project_id):
    # Ensure user is a handyman
    if request.user.user_type != 'artisan':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux artisans.")
        return redirect('base:home')

    # Get or create handyman profile
    handyman, created = Handyman.objects.get_or_create(user=request.user)

    # Get the project
    project = get_object_or_404(Project, id=project_id)

    # Check if handyman can apply for this project
    if (project.service != request.user.service or
        project.region != request.user.region):
        messages.error(request, "Vous ne pouvez pas postuler pour ce projet car il ne correspond pas à votre service ou région.")
        return redirect('handyman:projects')

    # Check if project is available
    if project.status != 'published':
        messages.error(request, "Ce projet n'est plus disponible pour les candidatures.")
        return redirect('handyman:project_detail', project_id=project_id)

    # Check if handyman already has an offer for this project
    existing_offer = ProjectOffer.objects.filter(handyman=handyman, project=project).first()
    if existing_offer:
        messages.warning(request, "Vous avez déjà soumis une offre pour ce projet.")
        return redirect('handyman:project_detail', project_id=project_id)

    if request.method == 'POST':
        form = ProjectOfferForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    offer = form.save(commit=False)
                    offer.handyman = handyman
                    offer.project = project
                    offer.save()

                    # Create notification for customer
                    create_customer_notification(
                        customer=project.customer,
                        notification_type='new_offer',
                        title=f"Nouvelle offre pour '{project.name}'",
                        message=f"{handyman.user.first_name} {handyman.user.last_name} a soumis une offre pour votre projet '{project.name}'.",
                        project=project,
                        offer=offer
                    )

                    messages.success(request, "Votre offre a été soumise avec succès!")
                    return redirect('handyman:project_detail', project_id=project_id)
            except Exception as e:
                messages.error(request, f"Erreur lors de la soumission: {str(e)}")
    else:
        form = ProjectOfferForm()

    context = {
        'form': form,
        'project': project,
        'handyman': handyman,
    }

    return render(request, 'handyman/submit_offer.html', context)


@login_required
def edit_offer_view(request, project_id):
    # Ensure user is a handyman
    if request.user.user_type != 'artisan':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux artisans.")
        return redirect('base:home')

    # Get or create handyman profile
    handyman, created = Handyman.objects.get_or_create(user=request.user)

    # Get the project
    project = get_object_or_404(Project, id=project_id)

    # Get the existing offer
    offer = get_object_or_404(ProjectOffer, handyman=handyman, project=project)

    # Check if offer can be edited (only pending offers)
    if offer.status != 'pending':
        messages.error(request, "Vous ne pouvez modifier que les offres en attente.")
        return redirect('handyman:project_detail', project_id=project_id)

    # Check if project is still available
    if project.status != 'published':
        messages.error(request, "Ce projet n'est plus disponible.")
        return redirect('handyman:project_detail', project_id=project_id)

    if request.method == 'POST':
        form = ProjectOfferForm(request.POST, instance=offer)
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_offer = form.save()

                    # Create notification for customer about offer update
                    create_customer_notification(
                        customer=project.customer,
                        notification_type='offer_update',
                        title=f"Offre mise à jour pour '{project.name}'",
                        message=f"{handyman.user.first_name} {handyman.user.last_name} a mis à jour son offre pour votre projet '{project.name}'.",
                        project=project,
                        offer=updated_offer
                    )

                    messages.success(request, "Votre offre a été mise à jour avec succès!")
                    return redirect('handyman:project_detail', project_id=project_id)
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    else:
        form = ProjectOfferForm(instance=offer)

    context = {
        'form': form,
        'project': project,
        'handyman': handyman,
        'offer': offer,
        'is_edit': True,
    }

    return render(request, 'handyman/submit_offer.html', context)
