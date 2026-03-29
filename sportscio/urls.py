from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("members/", views.members_view, name="members"),
    path("documents/", views.documents_view, name="documents"),
    path("profile/", views.profile_settings_view, name="profile_settings"),
    path("cio/", views.cio_profile_view, name="cio_profile"),
    path("user/", views.user_profile_view, name="user_profile"),
    path("exec/", views.exec_profile_view, name="exec_profile"),
    path("admin/", views.admin_profile_view, name="admin_profile"),
    path("user-roles/", views.user_role_admin_view, name="user_role_admin"),
    path("messages/", views.messages_view, name="messages"),
    path("messages/admin/", views.messages_admin_view, name="messages_admin"),
    path("announcements/", views.announcements_view, name="announcements"),
    path("api/announcements/create/", views.create_announcement, name="create_announcement"),
    path("api/announcements/", views.get_announcements, name="get_announcements"),
    path("exec/new-event/", views.new_event_view, name="new_event"),
]
