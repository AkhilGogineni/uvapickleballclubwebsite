from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role=Profile.ROLE_MEMBER)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


def assign_initial_role(user):
    profile, _ = Profile.objects.get_or_create(user=user)

    # Default: member.
    # User administrator accounts must be created through Django admin or direct DB updates,
    # not through the normal signup flow.
    profile.role = Profile.ROLE_MEMBER
    profile.save(update_fields=["role"])


@receiver(user_signed_up)
def handle_google_signup(request, user, **kwargs):
    assign_initial_role(user)
