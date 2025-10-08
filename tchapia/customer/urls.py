from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('post-project/', views.post_project_view, name='post_project'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('project/<int:project_id>/edit/', views.project_edit_view, name='project_edit'),
    path('project/<int:project_id>/delete/', views.project_delete_view, name='project_delete'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]