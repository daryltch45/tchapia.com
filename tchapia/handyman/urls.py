from django.urls import path
from . import views

app_name = 'handyman'

urlpatterns = [
    path('projects/', views.projects_view, name='projects'),
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('project/<int:project_id>/offer/', views.submit_offer_view, name='submit_offer'),
    path('project/<int:project_id>/offer/edit/', views.edit_offer_view, name='edit_offer'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]