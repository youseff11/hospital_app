# users/permissions.py
from rest_framework.permissions import BasePermission

class IsRealAdmin(BasePermission):
    """
    يسمح فقط للمستخدم اللي role بتاعه = ADMIN في UserProfile
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        try:
            profile = user.userprofile
        except:
            return False

        return profile.user_type == "ADMIN"
