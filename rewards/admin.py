# rewards/admin.py
from django.contrib import admin
from .models import CitizenProfile, PointsTransaction, Reward, RewardRedemption

admin.site.register(CitizenProfile)
admin.site.register(Reward)
admin.site.register(RewardRedemption)
admin.site.register(PointsTransaction)



