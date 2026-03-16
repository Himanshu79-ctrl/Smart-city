from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CitizenRewardProfile, Reward, RewardRedemption, PointsTransaction

@login_required
def rewards_dashboard(request):
    profile, created = CitizenRewardProfile.objects.get_or_create(user=request.user)
    transactions = PointsTransaction.objects.filter(user=request.user).order_by('-created_at')
    available_rewards = Reward.objects.all()
    
    context = {
        'profile': profile,
        'transactions': transactions,
        'available_rewards': available_rewards,
        'user_levels': {
            'beginner': 'Beginner (0-99 points)',
            'contributor': 'Contributor (100-499 points)',
            'champion': 'Champion (500-999 points)',
            'hero': 'Hero (1000+ points)'
        }
    }
    return render(request, 'rewards/rewards_dashboard.html', context)

@login_required
def rewards_list(request):
    rewards = Reward.objects.filter(is_active=True, stock__gt=0)
    profile = CitizenRewardProfile.objects.get(user=request.user)
    
    return render(request, 'rewards/rewards_list.html', {
        'rewards': rewards,
        'user_points': profile.total_points
    })

@login_required
def redeem_reward(request, reward_id):
    if request.method == 'POST':
        try:
            reward = Reward.objects.get(id=reward_id, is_active=True, stock__gt=0)
            profile = CitizenRewardProfile.objects.get(user=request.user)
            
            if profile.total_points >= reward.points_required:
                # Create redemption
                redemption = RewardRedemption.objects.create(
                    user=request.user,
                    reward=reward,
                    points_used=reward.points_required
                )
                
                # Deduct points
                profile.total_points -= reward.points_required
                profile.update_level()
                profile.save()
                
                # Reduce stock
                reward.stock -= 1
                reward.save()
                
                # Record transaction
                PointsTransaction.objects.create(
                    user=request.user,
                    transaction_type='reward_claimed',
                    points=-reward.points_required,
                    description=f'Redeemed: {reward.name}',
                )
                
                messages.success(request, f'Successfully redeemed {reward.name}!')
                return redirect('my_rewards')
            else:
                messages.error(request, 'Not enough points to redeem this reward.')
                
        except Reward.DoesNotExist:
            messages.error(request, 'Reward not available.')
    
    return redirect('rewards_list')

@login_required
def my_rewards(request):
    redemptions = RewardRedemption.objects.filter(user=request.user).order_by('-redeemed_at')
    return render(request, 'rewards/my_rewards.html', {'redemptions': redemptions})

@login_required
def leaderboard(request):
    top_citizens = CitizenRewardProfile.objects.order_by('-total_points')[:20]
    return render(request, 'rewards/leaderboard.html', {'top_citizens': top_citizens})