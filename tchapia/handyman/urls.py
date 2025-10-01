from django.urls import path
from . import views

app_name = 'handyman'

urlpatterns = [
    path('projects/', views.projects_view, name='projects'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]