"""App-level roles: member, officer, user_admin (see course spec)."""
from .models import Profile


def _profile(user):
    if not user.is_authenticated:
        return None
    try:
        return user.profile
    except Profile.DoesNotExist:
        return None


def is_officer(user):
    p = _profile(user)
    return p is not None and p.role == Profile.ROLE_OFFICER


def is_user_admin(user):
    p = _profile(user)
    return p is not None and p.role == Profile.ROLE_USER_ADMIN


def is_member(user):
    p = _profile(user)
    return p is not None and p.role == Profile.ROLE_MEMBER


def is_privileged(user):
    """Officer tools + Django superuser (same UI shell for now)."""
    return is_officer(user) or (user.is_authenticated and user.is_superuser)
