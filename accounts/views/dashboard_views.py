from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib import messages
from reports.models import IssueReport

User = get_user_model()


# ======================
# COMMON REDIRECT
# ======================
@login_required
def dashboard(request):
    return redirect("profile")


# ======================
# ADMIN DASHBOARD
# ======================
@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return redirect("profile")

    # 🔥 Optimized query (important for scaling)
    issues = IssueReport.objects.select_related(
        "citizen", "assigned_department", "category"
    ).prefetch_related("assigned_workers").order_by("-created_at")

    # ======================
    # FILTERS
    # ======================
    city = request.GET.get("city")
    status = request.GET.get("status")

    if city:
        issues = issues.filter(city__iexact=city)

    if status:
        issues = issues.filter(status=status)

    # ======================
    # STATS
    # ======================
    total_issues = IssueReport.objects.count()
    pending_issues = IssueReport.objects.filter(status="reported").count()
    resolved_issues = IssueReport.objects.filter(status="resolved").count()

    today_issues = IssueReport.objects.filter(
        created_at__date=timezone.now().date()
    ).count()

    total_staff = User.objects.filter(user_type="department_staff").count()
    total_citizens = User.objects.filter(user_type="citizen").count()

    # city filter dropdown
    all_cities = (
        IssueReport.objects
        .exclude(city__isnull=True)
        .exclude(city="")
        .values_list("city", flat=True)
        .distinct()
    )

    context = {
        "issues": issues[:10],  # latest 10
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
# STAFF DASHBOARD
# ======================
@login_required
def staff_dashboard(request):

    # ❌ wrong user access
    if request.user.user_type != "department_staff":
        return redirect("profile")

    # ❌ worker missing (edge case)
    if not hasattr(request.user, 'worker'):
        messages.error(request, "Staff profile not found.")
        return redirect("profile")

    # 🔥 correct filtering
    issues = IssueReport.objects.select_related(
        "citizen", "assigned_department"
    ).filter(
        assigned_department=request.user.worker.department
    ).order_by("-created_at")

    context = {
        "issues": issues
    }

    return render(request, "staff/dashboard.html", context)


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

            # 🔥 auto resolved time
            if new_status == "resolved":
                issue.resolved_at = timezone.now()

            issue.save()

            messages.success(request, "Issue status updated successfully.")

    return redirect("admin_dashboard")