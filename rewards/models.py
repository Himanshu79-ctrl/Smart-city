from django.db import models
from django.utils import timezone
from accounts.models import CustomUser

class CitizenProfile(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('contributor', 'Contributor'),
        ('champion', 'Champion'),
        ('hero', 'Hero'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    issues_reported = models.IntegerField(default=0)
    issues_resolved = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"
    
    def update_level(self):
        if self.total_points >= 1000:
            self.level = 'hero'
        elif self.total_points >= 500:
            self.level = 'champion'
        elif self.total_points >= 100:
            self.level = 'contributor'
        else:
            self.level = 'beginner'

class PointsTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('issue_reported', 'Issue Reported'),
        ('issue_resolved', 'Issue Resolved'),
        ('reward_claimed', 'Reward Claimed'),
        ('bonus', 'Bonus'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()
    description = models.TextField()
    related_issue = models.ForeignKey('reports.IssueReport', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.points} points"

class Reward(models.Model):
    REWARD_TYPES = [
        ('movie_ticket', 'Movie Ticket'),
        ('shopping_voucher', 'Shopping Voucher'),
        ('food_coupon', 'Food Coupon'),
        ('gift_card', 'Gift Card'),
        ('cashback', 'Cashback'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    points_required = models.IntegerField()
    image = models.ImageField(upload_to='rewards/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField(default=0)
    validity_days = models.IntegerField(default=30)
    
    def __str__(self):
        return self.name

class RewardRedemption(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_used = models.IntegerField()
    redeemed_at = models.DateTimeField(auto_now_add=True)
    is_fulfilled = models.BooleanField(default=False)
    fulfillment_date = models.DateTimeField(null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"