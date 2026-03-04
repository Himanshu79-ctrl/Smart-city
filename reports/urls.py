from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.report_issue, name='report_issue'),
    path('track/<str:tracking_id>/', views.track_issue, name='track_issue'),
    path('my-issues/', views.my_issues, name='my_issues'),
    path('city-issues/', views.city_issues, name='city_issues'),
    path('vote_issue/<int:issue_id>/', views.vote_issue, name='vote_issue'),
    path('comment/<int:issue_id>/', views.add_comment, name='add_comment'),
    path('emergency/', views.emergency_page, name='emergency_page'),
    path('emergency/report/', views.report_emergency, name='report_emergency'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)