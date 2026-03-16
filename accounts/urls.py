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
     # 🔥 PASSWORD RESET URLS - YEH ADD KARO
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             html_email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path("profile/edit/", views.edit_profile, name="edit_profile"),
]