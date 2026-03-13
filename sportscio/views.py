from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


#User (student)
@login_required
def user_profile_view(request, user=None):
    """
    Landing page for a regular club member.
    Shows announcements and schedule.
    """
    #Dummy data
    announcements = [
        "Soccer practice moved to Tuesday 5 PM",
        "Basketball tournament registration open",
        "Reminder: Club fees due next week"
    ]

    schedule = [
        {"day": "Monday", "event": "Soccer practice", "time": "5:00 PM"},
        {"day": "Wednesday", "event": "Basketball practice", "time": "6:30 PM"},
        {"day": "Friday", "event": "Club meeting", "time": "7:00 PM"}
    ]

    context = {
        "username": getattr(user, "username", "Demo Member"),
        "user_type": getattr(user, "user_type", "member"),
        "announcements": announcements,
        "schedule": schedule,
    }

    return render(request, "profile_user.html", context)


#CIO admin
@login_required
def cio_profile_view(request, user=None):
    context = {
        "username": getattr(user, "username", "Demo CIO"),
        "user_type": "CIO",
        "email": getattr(user, "email", "cio@example.com"),
        "applications": ["App 1", "App 2", "App 3"],  # placeholder for demo
    }
    return render(request, "profile_cio.html", context)


#Superuser
@login_required
def admin_profile_view(request, user=None):
    context = {
        "username": getattr(user, "username", "Admin"),
        "user_type": "superuser",
        "email": getattr(user, "email", "admin@example.com"),
        "all_users": ["alice", "bob", "charlie"],  # placeholder list
    }
    return render(request, "profile_admin.html", context)

def home(request):
    user = request.user
    
    if user.is_superuser:
        return redirect('admin_profile')
    
    try:
        profile = user.profile
    except:
        return redirect('login')
    
    if profile.user_type == 'exec':
        return redirect('cio_profile')
    else:
        return redirect('user_profile')
    
    # announcements = [
    #     "Tryouts begin next Monday",
    #     "Team meeting Friday at 6pm"
    # ]

    # schedule = [
    #     {"day": "Monday", "event": "Practice", "time": "5:00 PM"},
    #     {"day": "Wednesday", "event": "Scrimmage", "time": "6:30 PM"}
    # ]

    # return render(request, "home.html", {
    #     "announcements": announcements,
    #     "schedule": schedule
    # })