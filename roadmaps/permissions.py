from rest_framework.permissions import BasePermission


class IsInstructorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # Anyone can view
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Must be logged in
        if not request.user.is_authenticated:
            return False

        role = getattr(request.user, "effective_role", None)
        return role in ["instructor", "admin"]