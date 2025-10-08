from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import Http404, JsonResponse
from .forms import PostProjectForm, CustomerProfileForm, CustomerUserProfileForm
from .models import Customer, Project, ProjectImage
from handyman.models import Handyman, HandymanNotification
from userauths.models import SERVICE_CHOICES

@login_required
def post_project_view(request):
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PostProjectForm(request.POST, request.FILES)
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

                    # Handle image uploads
                    images = form.cleaned_data.get('images', [])
                    if not isinstance(images, list):
                        images = [images] if images else []

                    for image in images:
                        if image:
                            ProjectImage.objects.create(
                                project=project,
                                image=image
                            )

                    # Get the selected service
                    selected_service = form.cleaned_data['service']

                    # Notify handymen in the same service and region
                    notification_count = notify_handymen(selected_service, project)

                    image_text = f" avec {len(images)} image(s)" if images else ""
                    messages.success(
                        request,
                        f"Projet '{project.name}' publié avec succès{image_text}! "
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

    # Get offers for this project
    offers = project.offers.all().select_related('handyman__user').order_by('-created_at')

    context = {
        'project': project,
        'customer': customer,
        'related_notifications': related_notifications,
        'offers': offers,
        'offers_count': offers.count(),
    }
    return render(request, 'customer/project_detail.html', context)

@login_required
def project_edit_view(request, project_id): 
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Get the project and ensure it belongs to the current user
    project = get_object_or_404(Project, id=project_id, customer=customer)

    if request.method == 'POST':
        form = PostProjectForm(request.POST, request.FILES, instance=project)
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

                    # Handle new image uploads
                    images = form.cleaned_data.get('images', [])
                    if not isinstance(images, list):
                        images = [images] if images else []

                    for image in images:
                        if image:
                            ProjectImage.objects.create(
                                project=updated_project,
                                image=image
                            )

                    # Check if service changed and notify new handymen if needed
                    selected_service = form.cleaned_data['service']
                    if project.status == 'published':
                        # Create update notifications
                        notification_count = notification_count = notify_handymen(selected_service, project)

                        image_text = f" avec {len(images)} nouvelle(s) image(s)" if images else ""
                        messages.success(
                            request,
                            f"Projet '{updated_project.name}' mis à jour avec succès{image_text}! "
                            f"{notification_count} artisan(s) ont été notifié(s) de la modification."
                        )
                    else:
                        image_text = f" avec {len(images)} nouvelle(s) image(s)" if images else ""
                        messages.success(request, f"Projet '{updated_project.name}' mis à jour avec succès{image_text}!")

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

@login_required
def profile_edit_view(request):
    # Ensure user is a customer
    if request.user.user_type != 'client':
        messages.error(request, "Accès non autorisé. Cette page est réservée aux clients.")
        return redirect('base:home')

    # Get or create customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = CustomerUserProfileForm(request.POST, instance=request.user)
        customer_form = CustomerProfileForm(request.POST, instance=customer)

        if user_form.is_valid() and customer_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    customer_form.save()
                    messages.success(request, "Profil mis à jour avec succès!")
                    return redirect('customer:profile_edit')
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    else:
        user_form = CustomerUserProfileForm(instance=request.user)
        customer_form = CustomerProfileForm(instance=customer)

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'customer': customer,
    }
    return render(request, 'customer/profile_edit.html', context)


@login_required
def project_delete_view(request, project_id):
    # Ensure user has customer profile
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Get the project and ensure it belongs to the current user
    project = get_object_or_404(Project, id=project_id, customer=customer)

    # Check if project can be deleted (only draft or published projects)
    if project.status in ['in_progress', 'completed']:
        messages.error(request, "Vous ne pouvez pas supprimer un projet en cours ou terminé.")
        return redirect('customer:dashboard')

    if request.method == 'POST':
        try:
            project_name = project.name
            project.delete()
            messages.success(request, f"Le projet '{project_name}' a été supprimé avec succès.")
            return redirect('customer:dashboard')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
            return redirect('customer:dashboard')

    # If not POST, redirect to dashboard
    return redirect('customer:dashboard')


def notify_handymen(service, project): 
    handymen_to_notify = Handyman.objects.filter(
        user__service=service,
        user__region=project.region,
        availability=True
    ).select_related('user')

    print("############# Handymen: ", handymen_to_notify)
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
    
    return notification_count


