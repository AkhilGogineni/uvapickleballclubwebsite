from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up, user_logged_in

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, user_type='student')


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


def assign_user_type(user):
    profile, _ = Profile.objects.get_or_create(user=user)

    exec_emails = getattr(settings, "CLUB_EXEC_EMAILS", [])

    if user.email in exec_emails:
        profile.user_type = "exec"
    else:
        profile.user_type = "student"

    profile.save()


@receiver(user_signed_up)
def handle_google_signup(request, user, **kwargs):
    assign_user_type(user)


@receiver(user_logged_in)
def handle_google_login(request, user, **kwargs):
    assign_user_type(user)