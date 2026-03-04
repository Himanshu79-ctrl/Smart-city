# accounts/admin.py
from django.contrib import admin
from .models import CustomUser, Department,Worker

admin.site.register(CustomUser)
admin.site.register(Department)
admin.site.register(Worker)