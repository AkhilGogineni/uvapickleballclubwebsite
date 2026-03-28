from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from .models import Message, Announcement


def is_exec(user):
    return hasattr(user, "profile") and user.profile.user_type == "exec"


@login_required
def home(request):
    user = request.user

    if user.is_superuser:
        return redirect("admin_profile")

    if hasattr(user, "profile") and user.profile.user_type == "exec":
        return redirect("exec_profile")

    return redirect("user_profile")


@login_required
def user_profile_view(request):
    return render(request, "profile_user.html")

@login_required
def messages_view(request):
    messages = Message.objects.filter(room='general').order_by('-timestamp')[:50][::-1]
    return render(request, "messages.html", {'messages': messages})

@login_required
@user_passes_test(is_exec)
def exec_profile_view(request):
    return render(request, "profile_exec.html")


@login_required
def admin_profile_view(request):
    if not request.user.is_superuser:
        return redirect("home")
    return render(request, "profile_admin.html")


@login_required
def announcements_view(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, "announcements.html", {'announcements': announcements})


@login_required
@require_http_methods(["POST"])
def create_announcement(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Only admins can create announcements'}, status=403)
    
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return JsonResponse({'error': 'Title and content required'}, status=400)

        announcement = Announcement.objects.create(
            author=request.user,
            title=title,
            content=content
        )

        # Broadcast to all connected announcement clients
        from .consumers import announcement_consumers
        broadcast_message = {
            'type': 'announcement_message',
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'author': announcement.author.username,
            'created_at': announcement.created_at.isoformat(),
        }
        
        # Async broadcast to all connected consumers
        import asyncio
        async def broadcast():
            for consumer in announcement_consumers:
                await consumer.announcement_message(broadcast_message)
        
        try:
            asyncio.run(broadcast())
        except RuntimeError:
            from asgiref.sync import async_to_sync
            async_to_sync(broadcast)()

        return JsonResponse({
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'author': announcement.author.username,
            'created_at': announcement.created_at.isoformat(),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def get_announcements(request):
    announcements = Announcement.objects.filter(is_active=True).values(
        'id', 'title', 'content', 'content', 'author__username', 'created_at'
    )
    return JsonResponse(list(announcements), safe=False)
