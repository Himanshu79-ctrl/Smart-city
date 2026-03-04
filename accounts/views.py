from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reports.models import IssueReport
from .forms import CustomUserCreationForm
from rewards.models import CitizenProfile
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


# ======================
# SMART REDIRECT FUNCTION
# ======================
def redirect_user_dashboard(user):
    if user.is_superuser:
        return redirect("admin_dashboard")
    elif user.user_type == 'department_staff':
        return redirect('staff_dashboard')
    else:
        return redirect('dashboard')


# ======================
# REGISTER (Citizen Only)
# ======================
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = 'citizen'
                user.save()

                CitizenProfile.objects.create(user=user)

                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect_user_dashboard(user)

            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ======================
# STAFF REGISTER (Only Superuser)
# ======================
def staff_register(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page!")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = 'department_staff'
                user.is_staff = True
                user.save()

                messages.success(request, 'Staff account created successfully!')
                return redirect("admin_dashboard")

            except Exception as e:
                messages.error(request, f'Error creating staff account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/staff_register.html', {'form': form})


# ======================
# LOGIN
# ======================
def custom_login(request):
    if request.user.is_authenticated:
        return redirect_user_dashboard(request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect_user_dashboard(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')


# ======================
# DASHBOARD (Citizen)
# ======================
@login_required
def dashboard(request):
    if request.user.user_type != 'citizen':
        return redirect_user_dashboard(request.user)

    return render(request, 'citizen_dashboard.html')


# ======================
# STAFF DASHBOARD
# ======================
@login_required
def staff_dashboard(request):
    if request.user.user_type != 'department_staff':
        return redirect_user_dashboard(request.user)

    issues = IssueReport.objects.filter(
        department=request.user.worker.department
    ).order_by('-created_at')

    return render(request, 'staff_dashboard.html', {'issues': issues})


# ======================
# ADMIN DASHBOARD (Superuser)
# ======================

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("dashboard")

    issues = IssueReport.objects.all().order_by("-created_at")

    # Filters
    city = request.GET.get("city")
    status = request.GET.get("status")

    if city:
        issues = issues.filter(city__iexact=city)

    if status:
        issues = issues.filter(status=status)

    # Stats
    total_issues = IssueReport.objects.count()
    pending_issues = IssueReport.objects.filter(status="pending").count()
    resolved_issues = IssueReport.objects.filter(status="resolved").count()
    today_issues = IssueReport.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    total_staff = User.objects.filter(user_type="department_staff").count()
    total_citizens = User.objects.filter(user_type="citizen").count()

    all_cities = IssueReport.objects.values_list("city", flat=True).distinct()

    context = {
        "issues": issues[:10],
        "total_issues": total_issues,
        "pending_issues": pending_issues,
        "resolved_issues": resolved_issues,
        "today_issues": today_issues,
        "total_staff": total_staff,
        "total_citizens": total_citizens,
        "all_cities": all_cities,
    }

    return render(request, "accounts/admin_dashboard.html", context)


# ======================
# UPDATE ISSUE STATUS (Admin Only)
# ======================
@login_required
def mark_issue_status(request, issue_id):
    if not request.user.is_superuser:
        return redirect('dashboard')

    issue = get_object_or_404(IssueReport, id=issue_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(IssueReport.STATUS_CHOICES):
            issue.status = new_status
            issue.save()
            messages.success(request, "Issue status updated successfully.")

    return redirect("admin_dashboard")


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')