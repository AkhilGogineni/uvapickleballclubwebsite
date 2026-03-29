from .models import Profile
from .permissions import is_privileged


def roles(request):
    if not request.user.is_authenticated:
        return {}
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return {
            "is_privileged": is_privileged(request.user),
            "is_officer": False,
            "is_user_admin": False,
        }
    return {
        "user_profile_obj": profile,
        "is_officer": profile.role == Profile.ROLE_OFFICER,
        "is_user_admin": profile.role == Profile.ROLE_USER_ADMIN,
        "is_privileged": is_privileged(request.user),
    }
