from django.shortcuts import redirect

from .permissions import is_user_admin


class UserAdministratorAppRestrictionMiddleware:
    """
    User Administrators may only access role management and auth/logout URLs,
    not the rest of the application (course requirement).
    """

    ALLOWED_PATH_PREFIXES = (
        "/sportscio/user-roles",
        "/logout",
        "/login",
        "/accounts/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and is_user_admin(request.user):
            path = request.path
            if path == "/favicon.ico":
                return self.get_response(request)
            if any(path.startswith(p) for p in self.ALLOWED_PATH_PREFIXES):
                return self.get_response(request)
            return redirect("user_role_admin")
        return self.get_response(request)
