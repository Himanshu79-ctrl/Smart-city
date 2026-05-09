from django.urls import path
from django.contrib.auth import views as django_auth_views

from .views import *

urlpatterns = [

    # ======================
    # AUTH
    # ======================
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', register, name='register'),

    # ======================
    # DASHBOARD
    # ======================
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),

    # ======================
    # PROFILE
    # ======================
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),

    # ======================
    # STAFF MANAGEMENT
    # ======================
    path('add-staff/', add_staff, name='add_staff'),
    path('staff/', staff_list, name='staff_list'),
    path('staff/<int:id>/', staff_detail, name='staff_detail'),
    path('staff/delete/<int:id>/', delete_staff, name='delete_staff'),

    # ======================
    # ISSUE MANAGEMENT
    # ======================
    path('admin/mark-issue/<int:issue_id>/', mark_issue_status, name='mark_issue_status'),

    # ======================
    # PASSWORD RESET
    # ======================
    path(
        'password-reset/',
        django_auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset.html',
            email_template_name='registration/password_reset_email.html',
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url='/accounts/password-reset/done/'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        django_auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'password-reset/<uidb64>/<token>/',
        django_auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/accounts/password-reset/complete/'
        ),
        name='password_reset_confirm'
    ),

    path(
        'password-reset/complete/',
        django_auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]