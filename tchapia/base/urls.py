from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('handymen_list/', views.handymen_list_view, name='handymen_list'),
    path('handyman/<int:handyman_id>/', views.handyman_profile_view, name='handyman_profile'),
    path('services/', views.services_list_view, name='services_list'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
]