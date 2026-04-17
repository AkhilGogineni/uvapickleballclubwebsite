from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages as django_messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import connection
from datetime import date, datetime, time, timedelta
import calendar as pycal
import json
from .models import ClubDocument, Message, Announcement, Event, Profile
from .permissions import is_officer, is_user_admin, is_privileged


@login_required
def home(request):
    if is_user_admin(request.user):
        return redirect("user_role_admin")
    return redirect("dashboard")


@login_required
def whoami_view(request):
    try:
        profile = request.user.profile
        role = profile.role
    except Profile.DoesNotExist:
        role = None
    db = connection.settings_dict
    return JsonResponse(
        {
            "user_id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_authenticated": request.user.is_authenticated,
            "role": role,
            "is_user_admin": is_user_admin(request.user),
            "is_officer": is_officer(request.user),
            "is_superuser": request.user.is_superuser,
            "db_name": db.get("NAME"),
            "db_host": db.get("HOST"),
        }
    )


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

    today = timezone.localdate()
    try:
        y = int(request.GET.get("year", today.year))
        m = int(request.GET.get("month", today.month))
    except (ValueError, TypeError):
        y, m = today.year, today.month
    if m < 1 or m > 12:
        y, m = today.year, today.month
    if y < 1970 or y > 2100:
        y = today.year

    first_day = date(y, m, 1)
    last_n = pycal.monthrange(y, m)[1]
    last_day = date(y, m, last_n)

    start_dt = timezone.make_aware(datetime.combine(first_day, time.min))
    end_dt = timezone.make_aware(datetime.combine(last_day, time.max))

    events_qs = Event.objects.filter(
        start_time__lte=end_dt,
        end_time__gte=start_dt,
    ).order_by("start_time")

    by_day = {}
    for e in events_qs:
        sd = timezone.localtime(e.start_time).date()
        ed = timezone.localtime(e.end_time).date()
        d = max(sd, first_day)
        end = min(ed, last_day)
        while d <= end:
            by_day.setdefault(d.isoformat(), []).append(e)
            d += timedelta(days=1)

    cal = pycal.Calendar(firstweekday=pycal.SUNDAY)
    weeks = cal.monthdatescalendar(y, m)

    calendar_weeks = []
    for week in weeks:
        row = []
        for d in week:
            key = d.isoformat()
            row.append(
                {
                    "date": d,
                    "in_month": d.month == m and d.year == y,
                    "is_today": d == today,
                    "events": by_day.get(key, []),
                }
            )
        calendar_weeks.append(row)

    if m == 1:
        prev_y, prev_m = y - 1, 12
    else:
        prev_y, prev_m = y, m - 1
    if m == 12:
        next_y, next_m = y + 1, 1
    else:
        next_y, next_m = y, m + 1

    month_label = date(y, m, 1).strftime("%B %Y")

    return render(
        request,
        "calendar.html",
        {
            "nav_active": "calendar",
            "calendar_weeks": calendar_weeks,
            "month_label": month_label,
            "cal_year": y,
            "cal_month": m,
            "prev_y": prev_y,
            "prev_m": prev_m,
            "next_y": next_y,
            "next_m": next_m,
            "today": today,
        },
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

    docs = ClubDocument.objects.select_related("uploaded_by")

    if request.method == "POST":
        if not is_privileged(request.user):
            django_messages.error(request, "Only club leaders can upload documents.")
            return redirect("documents")
        title = request.POST.get("title", "").strip()
        upload = request.FILES.get("file")
        if not title or not upload:
            django_messages.error(request, "Title and file are required.")
            return redirect("documents")
        max_bytes = 15 * 1024 * 1024
        if upload.size > max_bytes:
            django_messages.error(request, "File must be 15MB or smaller.")
            return redirect("documents")
        ClubDocument.objects.create(
            uploaded_by=request.user,
            title=title[:200],
            file=upload,
        )
        django_messages.success(request, "Document uploaded.")
        return redirect("documents")

    return render(
        request,
        "documents.html",
        {"nav_active": "documents", "documents": docs},
    )


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
        phone = request.POST.get("phone_number", "").strip()
        
        # Checkboxes only sent if checked
        email_notifs = request.POST.get("email_notifications") == "on"
        sms_notifs = request.POST.get("sms_notifications") == "on"

        user.first_name = first[:150]
        user.last_name = last[:150]
        user.save(update_fields=["first_name", "last_name"])

        profile.phone_number = phone[:15]
        profile.email_notifications = email_notifs
        profile.sms_notifications = sms_notifs

        if birthday_raw:
            try:
                profile.birthday = datetime.strptime(birthday_raw, "%Y-%m-%d").date()
            except ValueError:
                django_messages.error(request, "Please use a valid birthday date.")
                return redirect("profile_settings")
        else:
            profile.birthday = None

        if "avatar" in request.FILES:
            img = request.FILES["avatar"]
            if img.size > 2 * 1024 * 1024:
                django_messages.error(request, "Profile photo must be 2MB or smaller.")
                return redirect("profile_settings")
            profile.avatar = img

        profile.save()
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
            {"error": "Only club leaders can create announcements"}, status=403
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
