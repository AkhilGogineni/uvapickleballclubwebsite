from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages as django_messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
import json
from .models import Message, Announcement, Event, Profile
from .permissions import is_officer, is_user_admin, is_privileged


@login_required
def home(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    return redirect("dashboard")


@login_required
def dashboard_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")

    announcements = Announcement.objects.filter(is_active=True).order_by("-created_at")[:5]
    now = timezone.now()
    events = (
        Event.objects.filter(start_time__gte=now).order_by("start_time")[:6]
    )
    if events.count() < 3:
        events = Event.objects.order_by("start_time")[:6]

    return render(
        request,
        "dashboard.html",
        {
            "announcements": announcements,
            "events": events,
            "nav_active": "dashboard",
        },
    )


@login_required
def calendar_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    events = Event.objects.order_by("start_time")
    return render(
        request,
        "calendar.html",
        {"events": events, "nav_active": "calendar"},
    )


@login_required
def members_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    users = User.objects.select_related("profile").order_by("username")
    return render(request, "members.html", {"users": users, "nav_active": "members"})


@login_required
def documents_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    return render(request, "documents.html", {"nav_active": "documents"})


@login_required
def profile_settings_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")

    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        first = request.POST.get("first_name", "").strip()
        last = request.POST.get("last_name", "").strip()
        birthday_raw = request.POST.get("birthday", "").strip()

        user.first_name = first[:150]
        user.last_name = last[:150]
        user.save(update_fields=["first_name", "last_name"])

        if birthday_raw:
            try:
                profile.birthday = datetime.strptime(birthday_raw, "%Y-%m-%d").date()
            except ValueError:
                django_messages.error(request, "Please use a valid birthday date.")
                return redirect("profile_settings")
        else:
            profile.birthday = None
        profile.save(update_fields=["birthday"])
        django_messages.success(request, "Your profile was updated.")
        return redirect("profile_settings")

    return render(
        request,
        "profile_settings.html",
        {"nav_active": "profile"},
    )


@login_required
def cio_profile_view(request):
    return redirect("dashboard")


@login_required
def user_profile_view(request):
    return redirect("dashboard")


@login_required
@user_passes_test(is_officer)
def exec_profile_view(request):
    return redirect("dashboard")


@login_required
def messages_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    msgs = (
        Message.objects.filter(room="general").order_by("-timestamp")[:50][::-1]
    )
    return render(
        request,
        "messages.html",
        {"messages": msgs, "nav_active": "messages", "chat_room": "general"},
    )


@login_required
@user_passes_test(is_privileged)
def messages_admin_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    msgs = Message.objects.filter(room="admin").order_by("-timestamp")[:50][::-1]
    return render(
        request,
        "messages_admin.html",
        {"messages": msgs, "nav_active": "messages_admin", "chat_room": "admin"},
    )


@login_required
@user_passes_test(is_privileged)
def new_event_view(request):
    error = None

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        start_time = request.POST.get("start_time", "").strip()
        end_time = request.POST.get("end_time", "").strip()
        description = request.POST.get("description", "").strip()

        if not title or not start_time or not end_time:
            error = "Title, start time, and end time are required."
        elif end_time <= start_time:
            error = "End time must be after start time."
        else:
            Event.objects.create(
                created_by=request.user,
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
            )
            return redirect("calendar")
    return render(
        request,
        "new_event.html",
        {"error": error, "nav_active": "calendar"},
    )


@login_required
def admin_profile_view(request):
    if not request.user.is_superuser:
        return redirect("home")
    return redirect("dashboard")


@login_required
@user_passes_test(is_user_admin)
def user_role_admin_view(request):
    if request.method == "POST":
        uid = request.POST.get("user_id")
        new_role = request.POST.get("new_role")
        if not uid or new_role not in (Profile.ROLE_MEMBER, Profile.ROLE_OFFICER):
            django_messages.error(request, "Invalid role change.")
            return redirect("user_role_admin")
        try:
            target = User.objects.select_related("profile").get(pk=uid)
        except User.DoesNotExist:
            django_messages.error(request, "User not found.")
            return redirect("user_role_admin")
        if not hasattr(target, "profile"):
            django_messages.error(request, "That user has no profile yet.")
            return redirect("user_role_admin")
        if target.profile.role == Profile.ROLE_USER_ADMIN:
            django_messages.error(
                request,
                "User administrator accounts cannot be changed in the application.",
            )
            return redirect("user_role_admin")
        target.profile.role = new_role
        target.profile.save(update_fields=["role"])
        django_messages.success(
            request,
            f"Updated {target.username} to {target.profile.get_role_display()}.",
        )
        return redirect("user_role_admin")

    users = User.objects.select_related("profile").order_by("username")
    return render(request, "user_role_admin.html", {"users": users})


@login_required
def announcements_view(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    announcements = Announcement.objects.filter(is_active=True)
    return render(
        request,
        "announcements.html",
        {"announcements": announcements, "nav_active": "announcements"},
    )


@login_required
@require_http_methods(["POST"])
def create_announcement(request):
    user = request.user
    if not (is_officer(user) or user.is_superuser):
        return JsonResponse(
            {"error": "Only officers can create announcements"}, status=403
        )

    try:
        data = json.loads(request.body)
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return JsonResponse({"error": "Title and content required"}, status=400)

        announcement = Announcement.objects.create(
            author=request.user,
            title=title,
            content=content,
        )

        from .consumers import announcement_consumers

        broadcast_message = {
            "type": "announcement_message",
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "author": announcement.author.username,
            "created_at": announcement.created_at.isoformat(),
        }

        import asyncio

        async def broadcast():
            for consumer in announcement_consumers:
                await consumer.announcement_message(broadcast_message)

        try:
            asyncio.run(broadcast())
        except RuntimeError:
            from asgiref.sync import async_to_sync

            async_to_sync(broadcast)()

        return JsonResponse(
            {
                "id": announcement.id,
                "title": announcement.title,
                "content": announcement.content,
                "author": announcement.author.username,
                "created_at": announcement.created_at.isoformat(),
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@login_required
def get_announcements(request):
    announcements = Announcement.objects.filter(is_active=True).values(
        "id", "title", "content", "content", "author__username", "created_at"
    )
    return JsonResponse(list(announcements), safe=False)
