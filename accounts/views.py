from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import CitizenProfile
from reports.models import IssueReport
from rewards.models import CitizenRewardProfile
from .forms import CustomUserCreationForm
from .utils.redirects import redirect_user_dashboard   # ✅ utils use

User = get_user_model()


# ======================
# REGISTER (Citizen Only)
# ======================

def register(request):

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "citizen"
            user.save()

            # profile ensure
            CitizenRewardProfile.objects.get_or_create(user=user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend') #it is because we have multiple backend authentication , so we will have to tell the django which will to use

            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

            messages.success(request, "Account created successfully!")

            return redirect_user_dashboard(user)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


# ======================
# STAFF REGISTER
# ======================

def staff_register(request):

    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page!")

    if request.method == "POST":

        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "department_staff"
            user.is_staff = True
            user.save()

            messages.success(request, "Staff account created successfully!")

            return redirect("admin_dashboard")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/staff_register.html", {"form": form})


# ======================
# LOGIN
# ======================

def custom_login(request):

    if request.user.is_authenticated:
        return redirect_user_dashboard(request.user)

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            if remember_me:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                messages.success(request, f"Welcome back, {username}! You will stay logged in for 2 weeks.")
            else:
                request.session.set_expiry(0)
                messages.info(request, "Session will expire when you close browser")

            return redirect_user_dashboard(user)

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


# ======================
# LOGOUT
# ======================

@login_required
def custom_logout(request):
    logout(request)
    return redirect("login")


# ======================
# CITIZEN DASHBOARD
# ======================

@login_required
def dashboard(request):
    return redirect("profile")


# ======================
# STAFF DASHBOARD
# ======================

@login_required
def staff_dashboard(request):

    if request.user.user_type != "department_staff":
        return redirect_user_dashboard(request.user)

    issues = IssueReport.objects.filter(
        department=request.user.worker.department
    ).order_by("-created_at")

    return render(request, "staff_dashboard.html", {"issues": issues})


# ======================
# ADMIN DASHBOARD
# ======================

@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("profile")

    issues = IssueReport.objects.all().order_by("-created_at")

    city = request.GET.get("city")
    status = request.GET.get("status")

    if city and city != "":
        issues = issues.filter(city__iexact=city)

    if status and status != "":
        issues = issues.filter(status=status)

    total_issues = IssueReport.objects.count()
    pending_issues = IssueReport.objects.filter(status="pending").count()
    resolved_issues = IssueReport.objects.filter(status="resolved").count()

    today_issues = IssueReport.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    total_staff = User.objects.filter(user_type="department_staff").count()
    total_citizens = User.objects.filter(user_type="citizen").count()

    all_cities = (
        IssueReport.objects
        .exclude(city__isnull=True)
        .exclude(city="")
        .values_list("city", flat=True)
    )

    context = {
        "issues": issues[:10],
        "total_issues": total_issues,
        "pending_issues": pending_issues,
        "resolved_issues": resolved_issues,
        "today_issues": today_issues,
        "total_staff": total_staff,
        "total_citizens": total_citizens,
        "all_cities": all_cities,
        "selected_city": city,
        "selected_status": status
    }

    return render(request, "accounts/admin_dashboard.html", context)


# ======================
# UPDATE ISSUE STATUS
# ======================

@login_required
def mark_issue_status(request, issue_id):

    if not request.user.is_superuser:
        return redirect("profile")

    issue = get_object_or_404(IssueReport, id=issue_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in dict(IssueReport.STATUS_CHOICES):
            issue.status = new_status
            issue.save()
            messages.success(request, "Issue status updated successfully.")

    return redirect("admin_dashboard")


# ======================
# PROFILE
# ======================

@login_required
def profile(request):
    return render(request, "accounts/profile.html")


# ======================
# EDIT PROFILE
# ======================

@login_required
def edit_profile(request):

    user = request.user

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if username:
            user.username = username

        if email:
            user.email = email

        if phone:
            user.phone = phone

        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get("profile_pic")

        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(
        request,
        "accounts/edit_profile.html",
        {"user": user}
    )