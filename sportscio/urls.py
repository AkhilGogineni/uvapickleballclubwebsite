from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("user/", views.user_profile_view, name="user_profile"),
    path("exec/", views.exec_profile_view, name="exec_profile"),
    path("admin/", views.admin_profile_view, name="admin_profile"),
    path("messages/", views.messages_view, name="messages"),
    path("announcements/", views.announcements_view, name="announcements"),
    path("api/announcements/create/", views.create_announcement, name="create_announcement"),
    path("api/announcements/", views.get_announcements, name="get_announcements"),
]