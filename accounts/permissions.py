from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
    """
    Разрешение, дающее доступ только пользователям с ролью admin.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
