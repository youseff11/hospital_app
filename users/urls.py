# users/urls.py (الكود الصحيح)

from django.urls import path
from .views import RegisterView, LoginView, DoctorProfileView # <== تم إضافته هنا

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('doctors/me/', DoctorProfileView.as_view(), name='doctor-profile-me'),
]