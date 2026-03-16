from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from .models import IssueReport, IssueCategory, EmergencyAlert, IssueVote, IssueComment
from accounts.models import Department
from rewards.models import CitizenRewardProfile, PointsTransaction
from django.db.models import Sum

def home(request):
    # Get top 5 recent issues with upvotes count
    recent_issues = IssueReport.objects.annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up'))
    ).order_by('-created_at')[:3]

    # Emergency alerts (already present)
    # emergency_alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')[:3]

    context = {
        'recent_issues': recent_issues,
        # 'emergency_alerts': emergency_alerts,
        # Baaki context agar ho toh yahan add karo
    }
    return render(request, 'reports/home.html', context)

@login_required
def profile(request):
    user = request.user

    # Reward Profile
    profile, created = CitizenRewardProfile.objects.get_or_create(user=user)

    reward_points = profile.total_points

    # User Issues
    user_issues = IssueReport.objects.filter(citizen=user)

    total_issues = user_issues.count()
    resolved_issues = user_issues.filter(status='resolved').count()
    in_progress_issues = user_issues.filter(status='in_progress').count()
    pending_issues = total_issues - resolved_issues

    # Monthly stats
    month_start = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    this_month_issues = user_issues.filter(
        created_at__gte=month_start
    ).count()

    this_month_points = PointsTransaction.objects.filter(
        user=user,
        created_at__gte=month_start,
        points__gt=0
    ).aggregate(total=Sum('points'))['total'] or 0

    context = {
        "profile": profile,
        "reward_points": reward_points,

        "total_issues": total_issues,
        "resolved_issues": resolved_issues,
        "in_progress_issues": in_progress_issues,
        "pending_issues": pending_issues,

        "recent_issues": user_issues.order_by("-created_at")[:5],

        "this_month_issues": this_month_issues,
        "this_month_points": this_month_points,
    }

    return render(request, "accounts/profile.html", context)

@login_required
def report_issue(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            category_name = request.POST.get('category')
            description = request.POST.get('description')
            location_address = request.POST.get('location_address')
            photo = request.FILES.get('photo') 
            
            print(f"Creating issue: {title}")
            
            # Get or create category
            category = IssueCategory.objects.first()
            if not category:
                department = Department.objects.first()
                if not department:
                    department = Department.objects.create(name="Public Works Department")
                
                category = IssueCategory.objects.create(
                    name="General",
                    department=department,
                    points=10
                )
            
            # Get department from category
            assigned_department = category.department
            
            # Create the issue
            issue = IssueReport.objects.create(
                citizen=request.user,
                title=title,
                description=description,
                category=category,
                location_address=location_address,
                assigned_department=assigned_department,
                status='reported',
                photo=photo,
            )
            
            # # Award points for reporting issue
            # try:
            #     profile = CitizenRewardProfile.objects.get(user=request.user)
            #     profile.issues_reported += 1
            #     profile.total_points += category.points
            #     profile.update_level()
            #     profile.save()
                
            #     PointsTransaction.objects.create(
            #         user=request.user,
            #         transaction_type='issue_reported',
            #         points=category.points,
            #         description=f'Points for reporting: {title}',
            #         related_issue=issue
            #     )
            # except Exception as e:
            #     print(f"Points error: {e}")
            
            print(f"Issue created: {issue.tracking_id}")
            messages.success(request, f'Issue reported successfully! Tracking ID: {issue.tracking_id}')
            return redirect('my_issues')
            
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f'Error: {str(e)}')
            return redirect('report_issue')
    
    return render(request, 'reports/report_issue.html')

@login_required
def city_issues(request):
    """Show all city issues with voting functionality"""
    # Get all issues with vote counts and user's votes
    issues = IssueReport.objects.annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count('votes', filter=Q(votes__vote_type='down')),
        comments_count=Count('comments')
    ).order_by('-created_at')
    
    # Get user's votes for each issue
    user_votes = {}
    for issue in issues:
        user_vote = issue.get_user_vote(request.user)
        user_votes[issue.id] = user_vote
    
    context = {
        'issues': issues,
        'user_votes': user_votes,
    }
    return render(request, 'reports/city_issues.html', context)

@login_required
def vote_issue(request, issue_id):
    """Handle issue voting"""
    if request.method == 'POST':
        issue = get_object_or_404(IssueReport, id=issue_id)
        vote_type = request.POST.get('vote_type')
        
        # Check if user already voted
        existing_vote = IssueVote.objects.filter(user=request.user, issue=issue).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote if clicking same button
                existing_vote.delete()
                action = 'removed'
            else:
                # Change vote type
                existing_vote.vote_type = vote_type
                existing_vote.save()
                action = 'changed'
        else:
            # Create new vote
            IssueVote.objects.create(user=request.user, issue=issue, vote_type=vote_type)
            action = 'added'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return JSON
            return JsonResponse({
                'success': True,
                'action': action,
                'upvotes': issue.get_upvotes_count(),
                'downvotes': issue.get_downvotes_count(),
                'score': issue.get_vote_score(),
                'user_vote': vote_type if action != 'removed' else None
            })
        else:
            messages.success(request, f'Vote {action}!')
            return redirect('city_issues')
    
    return redirect('city_issues')

@login_required
def add_comment(request, issue_id):
    """Add comment to issue"""
    if request.method == 'POST':
        issue = get_object_or_404(IssueReport, id=issue_id)
        comment_text = request.POST.get('comment')
        
        if comment_text.strip():
            IssueComment.objects.create(
                user=request.user,
                issue=issue,
                comment=comment_text
            )
            messages.success(request, 'Comment added successfully!')
        
        return redirect('city_issues')
    
    return redirect('city_issues')

@login_required
def track_issue(request, tracking_id):
    try:
        issue = IssueReport.objects.get(tracking_id=tracking_id)
        return render(request, 'reports/track_issue.html', {'issue': issue})
    except IssueReport.DoesNotExist:
        messages.error(request, 'Issue not found!')
        return redirect('my_issues')

@login_required
def my_issues(request):
    issues = IssueReport.objects.filter(citizen=request.user).order_by('-created_at')
    return render(request, 'reports/my_issues.html', {'issues': issues})

@login_required
def emergency_page(request):
    alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'reports/emergency_page.html', {'alerts': alerts})

@login_required
def report_emergency(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        
        EmergencyAlert.objects.create(
            title=title,
            description=description,
            location=location,
            reported_by=request.user,
            emergency_level='medium'
        )
        
        messages.success(request, 'Emergency alert reported successfully!')
        return redirect('emergency_page')
    
    return render(request, 'reports/report_emergency.html')