from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.rewards_dashboard, name='rewards_dashboard'),
    path('rewards/', views.rewards_list, name='rewards_list'),
    path('redeem/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
    path('my-rewards/', views.my_rewards, name='my_rewards'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]