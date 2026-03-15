from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect


def is_exec(user):
    return hasattr(user, "profile") and user.profile.user_type == "exec"


@login_required
def home(request):
    user = request.user

    if user.is_superuser:
        return redirect("admin_profile")

    if hasattr(user, "profile") and user.profile.user_type == "exec":
        return redirect("cio_profile")

    return redirect("user_profile")


@login_required
def user_profile_view(request):
    return render(request, "profile_user.html")

@login_required
def messages_view(request):
    return render(request, "messages.html")

@login_required
@user_passes_test(is_exec)
def cio_profile_view(request):
    return render(request, "profile_cio.html")


@login_required
def admin_profile_view(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request, "profile_admin.html")