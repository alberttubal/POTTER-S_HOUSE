from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not getattr(user, "is_active", False):
            return False
        return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))


class RBACPermission(BasePermission):
    def has_permission(self, request, view):
        permission_map = getattr(view, "permission_map", None)
        if not permission_map:
            return True

        required = permission_map.get(request.method)
        if not required:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_superuser", False):
            return True

        if isinstance(required, str):
            required = [required]
        return user.has_perms(required)
