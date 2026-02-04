# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # User Views
    RegisterView, LoginView, DoctorProfileView,
    AdminListUsers, AdminDeleteUser, AdminUpdateRole,
    # Medical Views (انتقلت هنا بعد الدمج)
    SpecializationViewSet, 
    DiseaseViewSet, 
    AppointmentViewSet,
    DoctorListView,
    DoctorsByDiseaseView,
    PatientListView
)

# إنشاء الـ Router للـ ViewSets
router = DefaultRouter()
router.register(r'specializations', SpecializationViewSet, basename='specialization')
router.register(r'diseases', DiseaseViewSet, basename='disease')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    # 1. الموجه التلقائي (Specializations, Diseases, Appointments)
    path('', include(router.urls)),

    # 2. مسارات الحسابات (Auth)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # 3. مسارات الأطباء (Doctors)
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/me/', DoctorProfileView.as_view(), name='doctor-profile-me'),
    path('doctors/by_disease/<int:disease_id>/', DoctorsByDiseaseView.as_view(), name='doctors-by-disease'),

    # 4. مسارات الإدارة (Admin)
    path("admin/list/", AdminListUsers.as_view()),
    path("admin/delete/<int:user_id>/", AdminDeleteUser.as_view()),
    path("admin/update-role/<int:user_id>/", AdminUpdateRole.as_view()),
    path('admin/patients/', PatientListView.as_view(), name='admin-patients-list'),
]