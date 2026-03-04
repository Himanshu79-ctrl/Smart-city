from django.db import models
from django.utils import timezone
from accounts.models import CustomUser, Department, Worker

class IssueCategory(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=10)
    
    def __str__(self):
        return self.name
    

class IssueReport(models.Model):
    # ... your existing fields ...
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('verified', 'Verified'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    citizen = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reported_issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE)
    
    location_address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    photo = models.ImageField(upload_to='issue_photos/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    assigned_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    assigned_workers = models.ManyToManyField(Worker, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    tracking_id = models.CharField(max_length=10, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            import random
            import string
            self.tracking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tracking_id} - {self.title}"
    
    def get_upvotes_count(self):
        return self.votes.filter(vote_type='up').count()
    
    def get_downvotes_count(self):
        return self.votes.filter(vote_type='down').count()
    
    def get_vote_score(self):
        return self.get_upvotes_count() - self.get_downvotes_count()
    
    def get_user_vote(self, user):
        try:
            return self.votes.get(user=user).vote_type
        except IssueVote.DoesNotExist:
            return None
    
    def get_comments_count(self):
        return self.comments.count()


class StatusUpdate(models.Model):
    issue = models.ForeignKey(IssueReport, on_delete=models.CASCADE, related_name='status_updates')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.issue.tracking_id} - {self.old_status} → {self.new_status}"

class EmergencyAlert(models.Model):
    EMERGENCY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.TextField()
    emergency_level = models.CharField(max_length=20, choices=EMERGENCY_LEVELS)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='emergency/photos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Emergency - {self.title}"
    

class IssueVote(models.Model):
    VOTE_TYPES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    issue = models.ForeignKey('IssueReport', on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'issue']  # One vote per user per issue
    
    def __str__(self):
        return f"{self.user.username} - {self.vote_type} - {self.issue.title}"

class IssueComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    issue = models.ForeignKey('IssueReport', on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.issue.title}"

# Add these methods to your existing IssueReport model






    


