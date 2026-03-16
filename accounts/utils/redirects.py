from django.shortcuts import redirect

def redirect_user_dashboard(user):

    if user.is_superuser:
        return redirect("admin_dashboard")

    if user.user_type == "department_staff":
        return redirect("staff_dashboard")

    return redirect("profile")