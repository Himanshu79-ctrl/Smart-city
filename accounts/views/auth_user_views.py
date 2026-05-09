from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model

from ..forms import CustomUserCreationForm
from ..utils.redirects import redirect_user_dashboard
from rewards.models import CitizenRewardProfile

User = get_user_model()


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


def custom_logout(request):
    logout(request)
    return redirect("login")