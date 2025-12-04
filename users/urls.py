# users/urls.py (الكود الصحيح)

from django.urls import path
from .views import RegisterView, LoginView, DoctorProfileView # <== تم إضافته هنا
from .views import AdminListUsers, AdminDeleteUser, AdminUpdateRole
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('doctors/me/', DoctorProfileView.as_view(), name='doctor-profile-me'),
    path("admin/list/", AdminListUsers.as_view()),
    path("admin/delete/<int:user_id>/", AdminDeleteUser.as_view()),
    path("admin/update-role/<int:user_id>/", AdminUpdateRole.as_view()),
]