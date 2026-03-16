# rewards/admin.py
from django.contrib import admin
from .models import CitizenRewardProfile, PointsTransaction, Reward, RewardRedemption

admin.site.register(CitizenRewardProfile)
admin.site.register(Reward)
admin.site.register(RewardRedemption)
admin.site.register(PointsTransaction)



