from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from .forms import PostProjectForm
from .models import Customer, Project
from handyman.models import Handyman, HandymanNotification
from userauths.models import SERVICE_CHOICES

@login_required
def post_project_view(request):
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PostProjectForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the project
                    project = form.save(commit=False)
                    project.customer = customer
                    project.status = 'published'

                    

                    # Handle optional budget fields
                    if not project.budget_min:
                        project.budget_min = 0
                    if not project.budget_max:
                        project.budget_max = 0

                    project.save()

                    # Get the selected service
                    selected_service = form.cleaned_data['service']

                    # Notify handymen in the same service and region
                    handymen_to_notify = Handyman.objects.filter(
                        user__service=selected_service,
                        user__region=project.region,
                        availability=True
                    ).select_related('user')

                    # Create notifications for handymen
                    notification_count = 0
                    for handyman in handymen_to_notify:
                        HandymanNotification.objects.create(
                            handyman=handyman,
                            notification_type='new_project',
                            title=f"Nouveau projet: {project.name}",
                            message=f"Un nouveau projet '{project.name}' a été publié dans votre région ({project.get_region_display()}) pour le service {handyman.user.get_service_display()}. Budget: {project.budget_range}",
                            project=project
                        )
                        notification_count += 1

                    messages.success(
                        request,
                        f"Projet '{project.name}' publié avec succès! "
                        f"{notification_count} artisan(s) ont été notifié(s)."
                    )
                    return redirect('customer:dashboard')

            except Exception as e:
                messages.error(request, f"Erreur lors de la publication: {str(e)}")

    else:
        form = PostProjectForm()

    context = {
        'form': form,
        'service_choices': SERVICE_CHOICES,
    }
    return render(request, 'customer/post_project.html', context)

@login_required
def dashboard_view(request):
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Get user's projects
    projects = Project.objects.filter(customer=customer).order_by('-created_at')

    context = {
        'customer': customer,
        'projects': projects,
    }
    return render(request, 'customer/dashboard.html', context)

@login_required
def project_detail_view(request, project_id):
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Get the project and ensure it belongs to the current user
    project = get_object_or_404(Project, id=project_id, customer=customer)

    # Get notifications related to this project (if any)
    related_notifications = HandymanNotification.objects.filter(project=project)

    context = {
        'project': project,
        'customer': customer,
        'related_notifications': related_notifications,
    }
    return render(request, 'customer/project_detail.html', context)

@login_required
def project_edit_view(request, project_id):
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Get the project and ensure it belongs to the current user
    project = get_object_or_404(Project, id=project_id, customer=customer)

    if request.method == 'POST':
        form = PostProjectForm(request.POST, instance=project)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Update the project
                    updated_project = form.save(commit=False)

                    # Handle optional budget fields
                    if not updated_project.budget_min:
                        updated_project.budget_min = 0
                    if not updated_project.budget_max:
                        updated_project.budget_max = 0

                    updated_project.save()

                    # Check if service changed and notify new handymen if needed
                    selected_service = form.cleaned_data['service']
                    if project.status == 'published':
                        # Only notify if project is still published
                        handymen_to_notify = Handyman.objects.filter(
                            user__service=selected_service,
                            user__region=updated_project.region,
                            availability=True
                        ).select_related('user')

                        # Create update notifications
                        notification_count = 0
                        for handyman in handymen_to_notify:
                            HandymanNotification.objects.create(
                                handyman=handyman,
                                notification_type='project_update',
                                title=f"Projet modifié: {updated_project.name}",
                                message=f"Le projet '{updated_project.name}' a été mis à jour. Budget: {updated_project.budget_range}",
                                project=updated_project
                            )
                            notification_count += 1

                        messages.success(
                            request,
                            f"Projet '{updated_project.name}' mis à jour avec succès! "
                            f"{notification_count} artisan(s) ont été notifié(s) de la modification."
                        )
                    else:
                        messages.success(request, f"Projet '{updated_project.name}' mis à jour avec succès!")

                    return redirect('customer:project_detail', project_id=project.id)

            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    else:
        # Pre-populate form with existing project data
        form = PostProjectForm(instance=project)
        
        print(f"################# {project.deadline} ###############") 

    context = {
        'form': form,
        'project': project,
        'customer': customer,
        'is_edit': True,
    }
    return render(request, 'customer/post_project.html', context)
