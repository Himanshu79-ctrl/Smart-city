from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('register/staff/', views.staff_register, name='staff_register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/mark_issue/<int:issue_id>/', views.mark_issue_status, name='mark_issue_status'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
]