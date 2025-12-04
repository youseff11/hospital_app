# users/urls.py

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    DoctorProfileView,
    AdminListUsers,
    AdminDeleteUser,
    AdminUpdateRole
)

urlpatterns = [
    path("users/register/", RegisterView.as_view()),
    path("users/login/", LoginView.as_view()),
    path("users/doctors/me/", DoctorProfileView.as_view()),

    # ADMIN
    path("admin/list/", AdminListUsers.as_view()),
    path("admin/delete/<int:user_id>/", AdminDeleteUser.as_view()),
    path("admin/update-role/<int:user_id>/", AdminUpdateRole.as_view()),
]
