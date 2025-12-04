# users/permissions.py

from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    يسمح بالوصول فقط إذا كان المستخدم هو ADMIN.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.userprofile.user_type == 'ADMIN')