from django.urls import path
from . import views

urlpatterns = [
    path("user/", views.user_profile_view, name="user_profile"),
    path("cio/", views.cio_profile_view, name="cio_profile"),
    path("admin/", views.admin_profile_view, name="admin_profile"),
]