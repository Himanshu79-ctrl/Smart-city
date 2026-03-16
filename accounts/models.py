from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('citizen', 'Citizen'),
        ('department_staff', 'Department Staff'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='citizen')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Department(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    description = models.TextField(blank=True)
    resolution_timeline = models.IntegerField(default=7)
    
    def __str__(self):
        return self.name

class Worker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="worker")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"
    
class CitizenProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return self.user.username