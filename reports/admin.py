# reports/admin.py
from django.contrib import admin
from .models import EmergencyAlert, IssueCategory, IssueReport, StatusUpdate

admin.site.register(IssueCategory)
admin.site.register(IssueReport)
admin.site.register(StatusUpdate)
admin.site.register(EmergencyAlert)