from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from customer.models import Project, CustomerNotification
from .models import Handyman, ProjectOffer, HandymanPortfolioImage
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
def projects_browse_view(request):
    # Ensure user is a handyman
    if request.user.user_type != 'artisan':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux artisans.")
        return redirect('base:home')

    # Get or create handyman profile
    handyman, created = Handyman.objects.get_or_create(user=request.user)

    # Get filter parameters
    service_filter = request.GET.get('service', '')
    region_filter = request.GET.get('region', '')
    city_filter = request.GET.get('city', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    budget_filter = request.GET.get('budget', '')

    # Start with base queryset - all published and in_progress projects
    projects = Project.objects.filter(
        status__in=['published', 'in_progress']
    ).select_related('customer__user').prefetch_related('project_images')

    # Apply filters
    if service_filter:
        projects = projects.filter(service=service_filter)
    else:
        # Default to handyman's service if no filter specified
        projects = projects.filter(service=request.user.service)

    if region_filter:
        projects = projects.filter(region=region_filter)
    else:
        # Default to handyman's region if no filter specified
        projects = projects.filter(region=request.user.region)

    if city_filter:
        projects = projects.filter(city=city_filter)

    if status_filter:
        projects = projects.filter(status=status_filter)

    if priority_filter:
        projects = projects.filter(priority=priority_filter)

    if budget_filter:
        if budget_filter == 'low':
            projects = projects.filter(budget_max__lte=50000)
        elif budget_filter == 'medium':
            projects = projects.filter(budget_max__gt=50000, budget_max__lte=200000)
        elif budget_filter == 'high':
            projects = projects.filter(budget_max__gt=200000)
        elif budget_filter == 'negotiable':
            projects = projects.filter(budget_max__isnull=True, budget_min__isnull=True)

    # Order by priority (urgent first) then by creation date
    projects = projects.order_by('-priority', '-created_at')

    # Get project count by status for all projects in handyman's service/region
    base_projects = Project.objects.filter(
        service=request.user.service,
        region=request.user.region,
        status__in=['published', 'in_progress']
    )

    total_projects = base_projects.count()
    published_projects = base_projects.filter(status='published').count()
    in_progress_projects = base_projects.filter(status='in_progress').count()

    # Import choices for filters
    from userauths.models import SERVICE_CHOICES, REGION_CHOICES, CITIES
    from customer.models import PRIORITY_CHOICES, PROJECT_STATUS_CHOICES

    context = {
        'handyman': handyman,
        'projects': projects,
        'total_projects': total_projects,
        'published_projects': published_projects,
        'in_progress_projects': in_progress_projects,
        # Filter choices
        'service_choices': SERVICE_CHOICES,
        'region_choices': REGION_CHOICES,
        'cities': CITIES,
        'priority_choices': PRIORITY_CHOICES,
        'status_choices': [('published', 'Publié'), ('in_progress', 'En cours')],
        'budget_choices': [
            ('low', 'Petit budget (< 50,000 XAF)'),
            ('medium', 'Budget moyen (50,000 - 200,000 XAF)'),
            ('high', 'Gros budget (> 200,000 XAF)'),
            ('negotiable', 'Budget à négocier'),
        ],
        # Current filter values
        'current_service': service_filter,
        'current_region': region_filter,
        'current_city': city_filter,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_budget': budget_filter,
    }
    return render(request, 'handyman/projects_browse.html', context)

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

                    # Handle portfolio image uploads
                    images = handyman_form.cleaned_data.get('portfolio_images', [])
                    if not isinstance(images, list):
                        images = [images] if images else []

                    for image in images:
                        if image:
                            HandymanPortfolioImage.objects.create(
                                handyman=handyman,
                                image=image
                            )

                    image_text = f" avec {len(images)} nouvelle(s) image(s)" if images else ""
                    messages.success(request, f"Profil mis à jour avec succès{image_text}!")
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
